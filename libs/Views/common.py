import os
from typing import Union

import mouse
from kivy.animation import Animation
from kivy.cache import Cache
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, ListProperty, ObjectProperty, NumericProperty, StringProperty, \
    ColorProperty, OptionProperty
from kivy.uix.behaviors import FocusBehavior, ButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.video import Video
from kivy.utils import escape_markup
from kivymd.app import MDApp
from kivymd.uix.behaviors import HoverBehavior, ScaleBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton, BaseButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog, BaseDialog
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu

import kivymd.material_resources as m_res
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.textfield import MDTextField

from libs.Common.utils import keycodes


class IconButton(ButtonBehavior, MDIcon):
    pass


class CustomVideo(Video):

    callback = ObjectProperty()

    def _on_load(self, *largs):
        self.loaded = True
        self._on_video_frame(largs)
        if self.callback:
            self.callback(init=True)


class TimeTip(MDCard):
    text = StringProperty('00:00:00')


class CustomVideoPlayer(MDBoxLayout):

    heightCalculated = NumericProperty(0)
    source = StringProperty('')
    preview = StringProperty('')
    state = OptionProperty('stop', options=['play', 'pause', 'stop'])
    progress = NumericProperty(0)
    text_progress = StringProperty('-')
    text_duration = StringProperty('-')
    fullscreen = BooleanProperty(False)
    _volume = NumericProperty(1)
    muted = BooleanProperty(False)

    def __init__(self, app):
        super(CustomVideoPlayer, self).__init__()
        self.last_mouse_pos_absolute = None
        self.app = app
        self.last_mouse_pos = (0, 0)
        self.video = self.ids.video
        self.video.callback = self.updateHeight
        self.controlsAnim = None
        self.hideControlsTask = None
        self.fbind('state', self.on_state)
        self.fbind('fullscreen', self.on_fullscreen_callback)
        os.environ['KIVY_VIDEO'] = 'ffpyplayer'
        Window.bind(mouse_pos=self.on_mouse_pos)
        Window.bind(size=self.updateHeightTask)
        self.progress_drag = False
        self.update_text_progress_task = None
        self._fullscreen_state = {}
        self.blockPause = True
        self.last_volume = 100

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        if value < 0:
            value = 0
            self.muted = True
        elif value > 1:
            value = 1
        else:
            self.muted = False
        self.video.volume = value
        self._volume = value

    def volume_muter(self):
        if self.volume != 0:
            self.last_volume = self.volume
            self.volume = 0
            self.muted = True
        else:
            if self.last_volume != 0:
                self.volume = self.last_volume
            else:
                self.volume = 1
            self.muted = False

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self.app.rootScreen.screenManager.current == 'item':
            if keycode[1] == 'escape':
                self.fullscreen = False
            elif keycode[1] == 'f':
                self.fullscreen = not self.fullscreen
            elif keycode[1] == 'spacebar':
                self.play_pause()
            elif keycode[1] in ['right', 'd']:
                self.showControls()
                self.planeHideControls()
                self.seekSeconds(10)
            elif keycode[1] in ['left', 'a']:
                self.showControls()
                self.planeHideControls()
                self.seekSeconds(-10)
            elif keycode[1] in ['up', 'w']:
                self.volume += 0.1
            elif keycode[1] in ['down', 's']:
                self.volume -= 0.1
            elif keycode[1] == 'm':
                self.volume_muter()
        return True

    def on_initialize(self):
        self.text_duration = self.progressToString()
        self.text_progress = self.progressToString(0)
        self.state = 'pause'

    def seekSeconds(self, increment):
        new_progress = (self.video.position + increment) / self.video.duration
        if new_progress < 0:
            new_progress = 0
        elif new_progress > 1:
            new_progress = 1
        self.toProgress(new_progress)

    def toProgress(self, progress):
        if progress < ((self.video.duration - 8) / self.video.duration):
            self.video.seek(progress)
            self.update_text_progress()
        else:
            self.videoDone()

    def videoDone(self, *args):
        self.text_duration = self.progressToString()
        self.text_progress = self.progressToString(0)
        self.video.seek(0)
        self.state = 'pause'
        self.update_text_progress(ending=True)
        self.showControls()

    def update_text_progress_caller(self, *args):
        if not self.progress_drag:
            self.update_text_progress()

    def update_text_progress(self, ending=False):
        if not ending and self.video.duration > 8 and self.video.position > self.video.duration - 8:
            self.videoDone()
        if self.progress_drag:
            self.text_progress = self.progressToString(self.progress)
        else:
            self.progress = round(100 * self.video.position / self.video.duration, 3)
            self.text_progress = self.progressToString(self.progress)

    def progressToString(self, progress=100):
        duration = self.video.duration * progress / 100
        hh = int((duration / 60) / 60)
        duration = duration - hh * 60 * 60
        mm = int((duration / 60))
        duration = duration - mm * 60
        ss = int(duration)
        if hh < 10:
            hh = f'0{hh}'
        if mm < 10:
            mm = f'0{mm}'
        if ss < 10:
            ss = f'0{ss}'
        string = f'{hh}:{mm}:{ss}'
        return string

    def play_pause(self):
        if self.blockPause:
            if self.state == 'pause' or self.state == 'stop':
                self.state = 'play'
            else:
                self.state = 'pause'

    def resumeUpdateTextTask(self, *args):
        self.update_text_progress_task = Clock.schedule_interval(self.update_text_progress_caller, 0.2)

    def moveMouseLow(self, *args):
        mouse.move(*self.last_mouse_pos_absolute, absolute=True, duration=0)
        self.showMouse()

    def moveMouse(self):
        Clock.schedule_once(self.moveMouseLow, 0.2)

    def on_fullscreen_callback(self, instance, value):
        window = self.get_parent_window()
        if not window:
            if value:
                self.fullscreen = False
            return
        if not self.parent:
            if value:
                self.fullscreen = False
            return

        if value:
            self._fullscreen_state = state = {
                'parent': self.parent,
                'pos': self.pos,
                'size': self.size,
                'pos_hint': self.pos_hint,
                'size_hint': self.size_hint,
                'window_children': window.children[:]}

            # remove all window children
            for child in window.children[:]:
                window.remove_widget(child)

            # put the video in fullscreen
            if state['parent'] is not window:
                state['parent'].remove_widget(self)
            window.add_widget(self)

            self.pos = (0, 0)
            self.size_hint = (1, 1)
            self.last_mouse_pos_absolute = mouse.get_position()
            self.hideMouse()
            Window.fullscreen = 'auto'
            self.moveMouse()
        else:
            state = self._fullscreen_state
            window.remove_widget(self)
            for child in state['window_children']:
                window.add_widget(child)
            self.pos_hint = state['pos_hint']
            self.size_hint = (1, None)
            self.pos = state['pos']
            self.size = state['size']
            if state['parent'] is not window:
                state['parent'].add_widget(self)
            self.last_mouse_pos_absolute = mouse.get_position()
            self.hideMouse()
            Window.fullscreen = False
            self.moveMouse()

    def on_touch_down(self, touch):
        super(CustomVideoPlayer, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.button == 'left':
            if self.collide_point(*touch.pos):
                if touch.is_double_tap:
                    self.fullscreen = not self.fullscreen
                if not self.ids.controls_panel.collide_point(*self.ids.controls_panel.to_widget(touch.pos[0], touch.pos[1])) or self.ids.controls.disabled:
                    self.play_pause()
        super(CustomVideoPlayer, self).on_touch_up(touch)

    def on_touch_up_progress(self, *args):
        if args[1].button == 'left':
            if self.ids.progress.collide_point(args[1].pos[0], args[1].pos[1]) or self.ids.progress.collide_point(args[1].pos[0] - dp(5), args[1].pos[1]) or self.ids.progress.collide_point(args[1].pos[0] + dp(5), args[1].pos[1]):
                self.progress = round(((args[1].pos[0] - (self.ids.controls_box.padding[0] + self.ids.btn_play_pause.width + dp(15))) / self.ids.progress.width) * 100, 3)
                if self.progress < 0:
                    self.progress = 0
                elif self.progress > 100:
                    self.progress = 100
                if self.update_text_progress_task:
                    self.update_text_progress_task.cancel()
                self.toProgress(self.progress / 100)
                Clock.schedule_once(self.resumeUpdateTextTask, 0.2)
        self.progress_drag = False

    def on_touch_down_progress(self, *args):
        if args[1].button == 'left':
            self.progress_drag = True
            if self.ids.progress.collide_point(args[1].pos[0], args[1].pos[1]) or self.ids.progress.collide_point(args[1].pos[0] - dp(5), args[1].pos[1]) or self.ids.progress.collide_point(args[1].pos[0] + dp(5), args[1].pos[1]):
                self.progress = round(((args[1].pos[0] - (self.ids.controls_box.padding[0] + self.ids.btn_play_pause.width + dp(15))) / self.ids.progress.width) * 100, 3)
                if self.progress < 0:
                    self.progress = 0
                elif self.progress > 100:
                    self.progress = 100
                self.update_text_progress()

    def on_touch_move_progress(self, *args):
        if args[1].button == 'left':
            if self.ids.progress.collide_point(args[1].pos[0], args[1].pos[1]) or self.ids.progress.collide_point(args[1].pos[0] - dp(5), args[1].pos[1]) or self.ids.progress.collide_point(args[1].pos[0] + dp(5), args[1].pos[1]):
                self.progress = round(((args[1].pos[0] - (self.ids.controls_box.padding[0] + self.ids.btn_play_pause.width + dp(15))) / self.ids.progress.width) * 100, 3)
                if self.progress < 0:
                    self.progress = 0
                elif self.progress > 100:
                    self.progress = 100
                self.update_text_progress()
            elif self.progress_drag and (self.ids.progress.collide_point(args[1].pos[0], self.ids.progress.center_y) or self.ids.progress.collide_point(args[1].pos[0] - dp(5), self.ids.progress.center_y) or self.ids.progress.collide_point(args[1].pos[0] + dp(5), self.ids.progress.center_y)):
                self.progress = round(((args[1].pos[0] - (self.ids.controls_box.padding[0] + self.ids.btn_play_pause.width + dp(15))) / self.ids.progress.width) * 100, 3)
                if self.progress < 0:
                    self.progress = 0
                elif self.progress > 100:
                    self.progress = 100
                self.update_text_progress()

    def on_mouse_pos(self, instance, pos):
        self.last_mouse_pos = pos
        if self.collide_point(*pos):
            if self.ids.controls_panel.collide_point(*self.ids.controls_panel.to_widget(*pos)):
                if self.hideControlsTask:
                    self.hideControlsTask.cancel()
                    self.hideControlsTask = None
                self.showControls()
            else:
                self.showControls()
                self.planeHideControls()
        if self.ids.progress.collide_point(*self.ids.progress.to_widget(*pos)):
            progress = round(((self.ids.progress.to_widget(pos[0], 0)[0] - (self.ids.controls_box.padding[0] + self.ids.btn_play_pause.width + dp(15))) / self.ids.progress.width) * 100, 3)
            self.ids.time_tip.text = self.progressToString(progress)
            self.ids.time_tip.pos = [(progress * self.ids.progress.width) / 100 + dp(10), self.ids.progress.center_y + dp(20)]
            if self.ids.time_tip.opacity == 0:
                self.ids.time_tip.opacity = 1
        else:
            if self.ids.time_tip.opacity == 1:
                Animation(opacity=0, d=0.1).start(self.ids.time_tip)

    def updateHeightTask(self, *args):
        self.updateHeight()

    def updateHeight(self, init=False):
        if init:
            self.on_initialize()
        video = self.video._video
        if video:
            ratio = video.texture.size[0] / video.texture.size[1]
            self.heightCalculated = self.width / ratio

    def showMouse(self, *args):
        Window.show_cursor = True

    def hideMouse(self, *args):
        if self.app.rootScreen.screenManager.current == 'item' and self.state == 'play' and self.collide_point(*self.last_mouse_pos):
            Window.show_cursor = False

    def showControls(self):
        self.showMouse()
        if self.ids.controls.disabled:
            self.ids.controls.disabled = False
            self.controlsAnim = Animation(opacity=1, d=0.1)
            self.controlsAnim.start(self.ids.controls)

    def hideControls(self, *args):
        if self.state == 'play' and not self.ids.controls.disabled:
            self.ids.controls.disabled = True
            self.controlsAnim = Animation(opacity=0, d=0.1)
            self.controlsAnim.start(self.ids.controls)
            Clock.schedule_once(self.hideMouse, 0.5)

    def planeHideControls(self, timeout=1.5):
        if self.hideControlsTask is None:
            self.hideControlsTask = Clock.schedule_once(self.hideControls, timeout)
        else:
            self.hideControlsTask.cancel()
            self.hideControlsTask = None
            self.planeHideControls(timeout)

    def on_state(self, *args):
        if args[1] == 'play':
            self.planeHideControls()
            if not self.update_text_progress_task:
                self.update_text_progress_task = Clock.schedule_interval(self.update_text_progress_caller, 0.2)
        else:
            if self.update_text_progress_task:
                self.update_text_progress_task.cancel()
                self.update_text_progress_task = None


def truncate_string(string, N, screen_brackets=False, no_space=True):
    out = string
    if len(string) > N:
        substring = string[0: N]
        if not no_space:
            last_alpha = 0
            for i in range(N - 1, 0, -1):
                if string[i - 1].isalpha() and not string[i].isalpha():
                    last_alpha = i
                    break
        else:
            last_alpha = N
        out = substring[0: last_alpha] + "…"

    if screen_brackets:
        out = out.replace('[', escape_markup('['))
        out = out.replace(']', escape_markup(']'))

    return out


class MDDialogModded(MDDialog):

    def __init__(self, key_handler=None, **kwargs):
        super().__init__(**kwargs)
        self.key_handler = key_handler
        self.isOpen = False
        Window.bind(on_keyboard=self.on_keyboard_handler)

    def on_keyboard_handler(self, _window, key, *_args):
        if self.key_handler:
            self.key_handler(_window, key)


class MDDialogConfirm(BaseDialog):
    title = StringProperty()
    text = StringProperty()
    buttons = ListProperty()
    items = ListProperty()
    width_offset = NumericProperty(dp(48))
    type = OptionProperty(
        "alert", options=["alert", "simple", "confirmation", "custom"]
    )
    md_bg_color = ColorProperty(None)

    def __init__(self, key_handler=None, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.update_width)

        if self.size_hint == [1, 1] and (
                m_res.DEVICE_TYPE == "desktop" or m_res.DEVICE_TYPE == "tablet"
        ):
            self.size_hint = (None, None)
            self.width = min(dp(560), Window.width - self.width_offset)
        elif self.size_hint == [1, 1] and m_res.DEVICE_TYPE == "mobile":
            self.size_hint = (None, None)
            self.width = min(dp(280), Window.width - self.width_offset)

        if not self.buttons:
            self.ids.root_button_box.height = 0
        else:
            self.create_buttons()

        self.key_handler = key_handler
        self.isOpen = False
        Window.bind(on_keyboard=self.on_keyboard_handler)

    def on_keyboard_handler(self, _window, key, *_args):
        if self.key_handler:
            self.key_handler(_window, key)

    def update_width(self, *args) -> None:
        self.width = max(
            self.height + self.width_offset,
            min(
                dp(560) if m_res.DEVICE_TYPE != "mobile" else dp(280),
                Window.width - self.width_offset,
            ),
        )

    def on_open(self) -> None:
        self.height = self.ids.container.height

    def create_buttons(self) -> None:
        for button in self.buttons:
            if issubclass(button.__class__, BaseButton):
                self.ids.button_box.add_widget(button)


class LDialogConfirm:

    def __init__(self, app):
        self.dialog = None
        self.app = app
        self.key = ''

        self._title = 'title'
        self._confirm_text = 'confirm_text'
        self._cancel_text = 'cancel_text'
        self._confirm_action = None
        self._text = 'text'
        self._arguments = ()

    def PreFinal(self, *args):
        self.dialog.opacity = 1

    def PreCache(self):
        self.RealOpen(pre=True)
        # self.Close()
        # Clock.schedule_once(self.PreFinal, 1)

    def on_keyboard(self, _window, key):
        if self.dialog.isOpen:
            if key == keycodes['enter']:
                self.Confirm()
                return True

    def RealOpen(self, pre=False):
        if not self.dialog:
            self.dialog = MDDialogConfirm(
                title=self._title,
                text=self._text,
                key_handler=self.on_keyboard,
                buttons=[
                    HoverMDFlatButton(
                        text=f'[b]{self._cancel_text}[/b]',
                        markup=True,
                        theme_text_color="Custom",
                        text_color=self.app.theme_cls.accent_color,
                        on_release=self.Close,
                    ),
                    HoverMDFlatButton(
                        theme_text_color="Custom",
                        markup=True,
                        text_color='#ef2a41',
                        text=f'[b]{self._confirm_text}[/b]',
                        on_release=self.Confirm,
                    )
                ]
            )
            self.dialog.ids.container.padding = [20, 20, 10, 0]
        if pre:
            self.key = 'MDDialogConfirm'
            Cache.append('precache', self.key, self.dialog)
        else:
            self.dialog.isOpen = True
            self.dialog.open()

    def Open(self, title='', confirm_text='CONFIRM', cancel_text='CANCEL', confirm_action=None, text='', arguments=None):
        changed = False
        if self._title != title:
            self._title = title
            changed = True
        if self._confirm_text != confirm_text:
            self._confirm_text = f'[b]{confirm_text}[/b]'
            changed = True
        if self._cancel_text != cancel_text:
            self._cancel_text = f'[b]{cancel_text}[/b]'
            changed = True
        if self._confirm_action != confirm_action:
            self._confirm_action = confirm_action
            changed = True
        if self._text != text:
            self._text = text
            changed = True
        if self._arguments != arguments:
            self._arguments = arguments
            changed = True
        if changed:
            self.Rebase()
        self.RealOpen()

    def Close(self, *args):
        self.dialog.isOpen = False
        self.dialog.dismiss(force=True)

    def Confirm(self, *args):
        if self._confirm_action:
            if self._arguments:
                self._confirm_action(*self._arguments)
            else:
                self._confirm_action()
        self.Close()

    def Rebase(self):
        self.dialog.title = self._title
        self.dialog.buttons[0].text = self._cancel_text
        self.dialog.buttons[1].text = self._confirm_text
        self.dialog.text = self._text


class LDialogEnterString:

    def __init__(self, app):
        self.dialog = None
        self.app = app
        self.key = ''

        self._validate_type = "all"
        self._title = 'title'
        self._confirm_text = 'confirm_text'
        self._cancel_text = 'cancel_text'
        self._confirm_action = None
        self._text = 'text'
        self._hint_text = 'hint_text'

    def PreFinal(self, *args):
        self.dialog.opacity = 1

    def PreCache(self):
        self.RealOpen(pre=True)
        # self.dialog.isOpen = False
        # self.dialog.dismiss(force=True)
        # Clock.schedule_once(self.PreFinal, 1)

    def on_keyboard(self, _window, key):
        if self.dialog.isOpen:
            if key == keycodes['enter']:
                self.Confirm()
                return True

    def RealOpen(self, pre=False):
        if not self.dialog:
            self.dialog = MDDialogModded(
                title=self._title,
                key_handler=self.on_keyboard,
                content_cls=MDTextField(text=self._text, hint_text=self._hint_text),
                type="custom",
                buttons=[
                    HoverMDFlatButton(
                        text=self._cancel_text,
                        theme_text_color="Custom",
                        text_color=self.app.theme_cls.primary_color,
                        on_release=self.Close,
                    ),
                    HoverMDFlatButton(
                        new_bg_color=self.app.theme_cls.primary_color,
                        theme_text_color="Custom",
                        text_color=self.app.theme_cls.bg_darkest,
                        text=self._confirm_text,
                        on_release=self.Confirm,
                    )
                ]
            )
        self.dialog.content_cls._hint_text_font_size = sp(10)
        if pre:
            self.key = 'MDDialogModded'
            Cache.append('precache', self.key, self.dialog)
        else:
            self.dialog.isOpen = True
            self.dialog.open()

    def Open(self, validate_type='all', title='', confirm_text='CONFIRM', cancel_text='CANCEL', confirm_action=None, text='', hint_text=''):
        changed = False
        if self._validate_type != validate_type:
            self._validate_type = validate_type
            changed = True
        if self._title != title:
            self._title = title
            changed = True
        if self._confirm_text != confirm_text:
            self._confirm_text = confirm_text
            changed = True
        if self._cancel_text != cancel_text:
            self._cancel_text = cancel_text
            changed = True
        if self._confirm_action != confirm_action:
            self._confirm_action = confirm_action
            changed = True
        if self._text != text:
            self._text = text
            changed = True
        if self._hint_text != hint_text:
            self._hint_text = hint_text
            changed = True
        if changed:
            self.Rebase()
        self.RealOpen()

    def Close(self, *args):
        self.dialog.content_cls.hint_text = self._hint_text
        self.dialog.isOpen = False
        self.dialog.dismiss(force=True)

    def getValidatedValue(self):
        s = self._text
        if 'int' in self._validate_type:
            s = int(s)
        elif 'float' in self._validate_type:
            self._text.replace(",", ".")
            s = float(s)
        return s

    def Validate(self):
        validate = True
        s = self._text
        if self._validate_type == 'int':
            validate = s.isdigit()
        elif self._validate_type == 'sint':
            if s[0] in ('-', '+'):
                validate = s[1:].isdigit()
            else:
                validate = s.isdigit()
        elif self._validate_type == 'float':
            self._text.replace(",", ".")
            validate = s.replace(".", "").isnumeric()
        elif self._validate_type == 'sfloat':
            self._text.replace(",", ".")
            if s[0] in ('-', '+'):
                validate = s[1:].replace(".", "").isnumeric()
            else:
                validate = s.replace(".", "").isnumeric()
        return validate

    def Confirm(self, *args):
        self._text = self.dialog.content_cls.text
        if self.Validate():
            self.Close()
            if self._confirm_action:
                self._confirm_action(self.getValidatedValue())
        else:
            self.dialog.content_cls.hint_text = f'Неверный ввод! Необходимый тип данных: {str(self._validate_type)}'

    def Rebase(self):
        self.dialog.title = self._title
        self.dialog.buttons[0].text = self._cancel_text
        self.dialog.buttons[1].text = self._confirm_text
        self.dialog.content_cls.text = self._text
        self.dialog.content_cls.hint_text = self._hint_text


class LoaderLabel(MDLabel):
    default_size_x = NumericProperty(100)
    default_size_y = NumericProperty(20)
    loading_color = ListProperty([0.15, 0.15, 0.15, 0.5])

    def __init__(self, **kwargs):
        super(LoaderLabel, self).__init__(**kwargs)
        self.bind(text=self.on_text_change)

    def on_text_change(self, instance, value):
        if value:
            self.loading_color = [1, 1, 1, 0.0]
        else:
            self.loading_color = [0.15, 0.15, 0.15, 0.5]


class DropdownMenuMod(MDDropdownMenu):

    grow_from_click = BooleanProperty(True)
    grow_start_pos = ListProperty([0, 0])
    grow_y_adjuster = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.md_menu.children[0].padding = [0, 0, 0, 0]
        self.last_touch = None

    def collide_point_custom(self, x, y):
        if self.menu.width > x and self.menu.height > y:
            return True
        else:
            return False

    def on_touch_down(self, touch):

        def temptouch(touch):
            if touch.button == 'right' or touch.button == 'left':
                if not self.collide_point_custom(touch.x, touch.y):
                    if self.caller:
                        self.caller.on_touch_up(touch, True)

        temptouch(touch)
        super().on_touch_down(touch)

    def open(self) -> None:

        def open(interval):
            if not self._calculate_complete:
                return

            position = self.adjust_position()

            if self.grow_from_click:
                self.menu.pos = self.grow_start_pos
                self.menu.x = self.grow_start_pos[0]
                self.menu.y = self.grow_start_pos[1] - (self.header_cls.height if self.header_cls else 0) - self.target_height + self.grow_y_adjuster
                self.menu.width = self.target_width
                self.menu.height = self.target_height
                self.menu.opacity = 1
            else:
                if position == "auto":
                    self.menu.pos = self._start_coords
                    anim = Animation(
                        x=self.tar_x,
                        y=self.tar_y
                          - (self.header_cls.height if self.header_cls else 0),
                        width=self.target_width,
                        height=self.target_height,
                        duration=self.opening_time,
                        opacity=1,
                        transition=self.opening_transition,
                    )
                    anim.start(self.menu)
                else:
                    if position == "center":
                        self.menu.pos = (
                            self._start_coords[0] - self.target_width / 2,
                            self._start_coords[1] - self.target_height / 2,
                        )
                    elif position == "bottom":
                        self.menu.pos = (
                            self._start_coords[0] - self.target_width / 2,
                            self.caller.pos[1] - self.target_height,
                        )
                    elif position == "top":
                        self.menu.pos = (
                            self._start_coords[0] - self.target_width / 2,
                            self.caller.pos[1] + self.caller.height,
                        )
                    anim = Animation(
                        width=self.target_width,
                        height=self.target_height,
                        duration=self.opening_time,
                        opacity=1,
                        transition=self.opening_transition,
                    )
                    anim.start(self.menu)
            if self not in Window.children:
                Window.add_widget(self)
            Clock.unschedule(open)
            self._calculate_process = False

        self.set_menu_properties()
        if not self._calculate_process:
            self._calculate_process = True
            Clock.schedule_interval(open, 0)

    def ajust_radius(self, interval: Union[int, float]) -> None:
        pass

    def set_menu_properties(self, interval: Union[int, float] = 0) -> None:
        """Sets the size and position for the menu window."""

        if self.caller:
            self.ids.md_menu.data = self.items
            # We need to pick a starting point, see how big we need to be,
            # and where to grow to.
            self._start_coords = self.caller.to_window(
                self.caller.center_x, self.caller.center_y
            )
            self.target_width = self.width_mult * m_res.STANDARD_INCREMENT

            # If we're wider than the Window...
            if self.target_width > Window.width:
                # ...reduce our multiplier to max allowed.
                self.target_width = (
                        int(Window.width / m_res.STANDARD_INCREMENT)
                        * m_res.STANDARD_INCREMENT
                )

            # Set the target_height of the menu depending on the size of
            # each MDMenuItem or MDMenuItemIcon.
            self.target_height = 0
            for item in self.ids.md_menu.data:
                self.target_height += item["height"]

            # self.target_height += dp(8)

            # If we're over max_height...
            if 0 < self.max_height < self.target_height:
                self.target_height = self.max_height

            # Establish vertical growth direction.
            if self.ver_growth is not None:
                ver_growth = self.ver_growth
            else:
                # If there's enough space below us:
                if (
                        self.target_height
                        <= self._start_coords[1] - self.border_margin
                ):
                    ver_growth = "down"
                # if there's enough space above us:
                elif (
                        self.target_height
                        < Window.height - self._start_coords[1] - self.border_margin
                ):
                    ver_growth = "up"
                # Otherwise, let's pick the one with more space and adjust
                # ourselves.
                else:
                    # If there"s more space below us:
                    if (
                            self._start_coords[1]
                            >= Window.height - self._start_coords[1]
                    ):
                        ver_growth = "down"
                        self.target_height = (
                                self._start_coords[1] - self.border_margin
                        )
                    # If there's more space above us:
                    else:
                        ver_growth = "up"
                        self.target_height = (
                                Window.height
                                - self._start_coords[1]
                                - self.border_margin
                        )

            if self.hor_growth is not None:
                hor_growth = self.hor_growth
            else:
                # If there's enough space to the right:
                if (
                        self.target_width
                        <= Window.width - self._start_coords[0] - self.border_margin
                ):
                    hor_growth = "right"
                # if there's enough space to the left:
                elif (
                        self.target_width
                        < self._start_coords[0] - self.border_margin
                ):
                    hor_growth = "left"
                # Otherwise, let's pick the one with more space and adjust
                # ourselves.
                else:
                    # if there"s more space to the right:
                    if (
                            Window.width - self._start_coords[0]
                            >= self._start_coords[0]
                    ):
                        hor_growth = "right"
                        self.target_width = (
                                Window.width
                                - self._start_coords[0]
                                - self.border_margin
                        )
                    # if there"s more space to the left:
                    else:
                        hor_growth = "left"
                        self.target_width = (
                                self._start_coords[0] - self.border_margin
                        )

            if ver_growth == "down":
                self.tar_y = self._start_coords[1] - self.target_height
            else:  # should always be "up"
                self.tar_y = self._start_coords[1]

            if hor_growth == "right":
                self.tar_x = self._start_coords[0]
            else:  # should always be "left"
                self.tar_x = self._start_coords[0] - self.target_width
            self._calculate_complete = True


class TextInputMod(TextInput):

    def __init__(self, **kwargs):
        super(TextInputMod, self).__init__(**kwargs)

        menu_items = [
            {
                "text": 'Выбрать все',
                "viewclass": "HoverOneLineListItem",
                "height": dp(40),
                "divider": None,
                "radius": [0, 0, 0, 0],
                "new_bg_color": [0, 0, 0, 0],
                "on_release": lambda: self.menu_callback('selectAll'),
            },
            {
                "text": 'Вырезать',
                "viewclass": "HoverOneLineListItem",
                "height": dp(40),
                "divider": None,
                "radius": [0, 0, 0, 0],
                "new_bg_color": [0, 0, 0, 0],
                "on_release": lambda: self.menu_callback('cut'),
            },
            {
                "text": 'Копировать',
                "viewclass": "HoverOneLineListItem",
                "height": dp(40),
                "divider": None,
                "radius": [0, 0, 0, 0],
                "new_bg_color": [0, 0, 0, 0],
                "on_release": lambda: self.menu_callback('copy'),
            },
            {
                "text": 'Вставить',
                "viewclass": "HoverOneLineListItem",
                "height": dp(40),
                "divider": None,
                "radius": [0, 0, 0, 0],
                "new_bg_color": [0, 0, 0, 0],
                "on_release": lambda: self.menu_callback('paste'),
            }
        ]

        self.menu = DropdownMenuMod(
            grow_from_click=True,
            grow_y_adjuster=dp(10),
            caller=self,
            opening_time=0.1,
            elevation=2,
            items=menu_items,
            width_mult=3,
            radius=dp(8),
        )

    def paste(self):
        data = Clipboard.paste().replace('\n', ' ')
        data = " ".join(data.split())
        self.delete_selection()
        self.insert_text(data)

    def menu_callback(self, action):
        if action == 'cut':
            self.focus = True
            self.cut()
            self.menu.dismiss()
            self.cancel_selection()
        elif action == 'copy':
            self.focus = True
            self.copy()
            self.menu.dismiss()
        elif action == 'paste':
            self.focus = True
            self.paste()
            self.menu.dismiss()
            self.cancel_selection()
        elif action == 'selectAll':
            self.focus = True
            self.select_all()
            self.menu.dismiss()

    def delete_selection(self, from_undo=False):
        self.cursor_width = 1
        super().delete_selection(from_undo)

    def _update_graphics_selection(self):
        super()._update_graphics_selection()
        if len(self.selection_text) > 0:
            self.cursor_color = [0, 0, 0, 0]
        else:
            self.cursor_color = MDApp.get_running_app().theme_cls.primary_color

    def cancel_selection(self):
        if self.menu in Window.children:
            pass
        else:
            super().cancel_selection()

    def select_all(self, *args):
        super(TextInputMod, self).select_all()

    def on_double_tap(self):
        Clock.schedule_once(self.select_all, 0)

    def on_touch_up(self, touch, menu_dismiss=False):
        if menu_dismiss:
            self.on_touch_up(touch)
        else:
            if touch.button == 'right':
                if self.collide_point(touch.x, touch.y):
                    self.menu.grow_start_pos = [touch.x + 5, touch.y]
                    self.menu.open()
                    # return
            super(TextInputMod, self).on_touch_up(touch)

    def on_touch_down(self, touch):
        if touch.button == 'right':
            if self.collide_point(touch.x, touch.y):
                if len(self.selection_text) > 0:
                    FocusBehavior.ignored_touch.append(touch)
                    return
        super(TextInputMod, self).on_touch_down(touch)


class HoverOneLineListItem(OneLineListItem, HoverBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids._lbl_primary.valign = 'center'
        self.ids._lbl_primary.size_hint_y = 1
        self.radius = [0, 0, 0, 0]


class HoverMDIconButton(MDIconButton, HoverBehavior):
    pass


class HoverMDFlatButton(MDFlatButton, HoverBehavior):
    pass


class NoHoverMDFlatButton(MDFlatButton, HoverBehavior):
    pass


class HoverMDBoxLayout(MDBoxLayout, HoverBehavior):
    pass


class HoverMDCardNoScale(MDCard, HoverBehavior):
    pass


class RoundedProgressBar(MDProgressBar):
    radius = ListProperty([dp(8), dp(8), dp(8), dp(8)])

    def check_size(self, interval: Union[int, float]) -> None:
        pass


class HoverMDCard(MDCard, HoverBehavior, ScaleBehavior):

    anim = ObjectProperty()

    def up_scale(self) -> None:
        self.anim = Animation(
            scale_value_x=1.01,
            scale_value_y=1.01,
            d=0.1,
        ).start(self)

    def normal_scale(self) -> None:
        self.anim = Animation(
            scale_value_x=1,
            scale_value_y=1,
            d=0.05,
        ).start(self)

    def on_enter(self):
        self.up_scale()

    def on_leave(self):
        self.normal_scale()


Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/common.kv"))
