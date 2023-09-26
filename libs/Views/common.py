import os
from typing import Union

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, ObjectProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.textinput import TextInput
from kivy.utils import escape_markup
from kivymd.app import MDApp
from kivymd.uix.behaviors import HoverBehavior, ScaleBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu

import kivymd.material_resources as m_res
from kivymd.uix.progressbar import MDProgressBar


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
