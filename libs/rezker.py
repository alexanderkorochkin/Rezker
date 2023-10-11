from kivy.cache import Cache
from kivy.clock import Clock, mainthread
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.loader import Loader
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty
from kivymd.app import MDApp

from libs.Common.database import DataManager
from libs.Common.utils import open_in_explorer, Spinner, SnackbarMod
from libs.Controllers.settings import SettingsController
from libs.Views.common import LDialogEnterString, LDialogConfirm
from libs.rootScreen import RootScreen

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class RezkerApp(MDApp):
    tooltip_show_delay = NumericProperty(0.3)
    COLS_LIBRARY = NumericProperty(5)

    dialogEnterString = ObjectProperty()

    msettings = ObjectProperty()
    settingsScreen = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = DataManager(self)
        self.msettings = SettingsController(app=self, name='settings')
        self.icon = 'res/icon.ico'
        self.rootScreen = None

        self.spinner = Spinner(self)

        self.dialogEnterString = LDialogEnterString(app=self)
        self.dialogConfirm = LDialogConfirm(app=self)

        self.settingsScreen = self.msettings.get_screen()

    def updateInfoTitle(self, *args):
        info = self.rootScreen.downloadsController.model.UpdateInfo
        if info:
            self.title = info
        else:
            self.title = 'Rezker'

    def get_type_color(self, sub_type):
        return '#696969' if 'аниме' in sub_type.lower() else '#216d2b' if 'мульт' in sub_type.lower() else '#df565a' if 'сериал' in sub_type.lower() else '#00a0b0'

    def provider(self, url: str = None):
        if url is not None:
            return url.replace('https://hdrezkawer.org', self.msettings.get('provider'))
        else:
            return self.msettings.get('provider')

    @staticmethod
    def open_in_explorer(path: str, mode):
        open_in_explorer(path, mode)

    @staticmethod
    def copy(link: str):
        Clipboard.copy(link)

    def on_resize(self, window, size):
        if size[0] < 400:
            self.COLS_LIBRARY = 2
        elif size[0] < 600:
            self.COLS_LIBRARY = 3
        elif size[0] < 900:
            self.COLS_LIBRARY = 4
        elif size[0] < 1300:
            self.COLS_LIBRARY = 5
        else:
            self.COLS_LIBRARY = 8

    def on_stop(self):
        self.rootScreen.downloadsController.on_close()

    def on_start(self):
        Config.set('graphics', 'resizable', True)
        Config.set('kivy', 'exit_on_escape', '0')
        Config.write()
        self.on_resize(Window, Window.size)
        self.PreCache()

    def build(self):

        Window.bind(size=self.on_resize)

        Factory.register('OpacityScrollEffectSmooth', module='libs.effects.opacityscrollsmooth')
        Loader.loading_image = 'assets/img/loading-image.png'

        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.set_colors("Orange", "300", "50", "800", "Gray", "600", "50", "800")

        self.rootScreen = RootScreen(app=self)
        self.spinner.start(Window, background_color=self.theme_cls.bg_dark, muted_screen=self.rootScreen)

        Clock.schedule_interval(self.updateInfoTitle, 1)

        return self.rootScreen

    @mainthread
    def callMessage(self, text):
        snackbar = SnackbarMod(self)
        snackbar.text = text
        snackbar.bg_color = self.theme_cls.bg_light
        snackbar.ids.text_bar.text_color = self.theme_cls.accent_color
        snackbar.ids.text_bar.text_style = 'Body1'

        snackbar.duration = 4
        snackbar.snackbar_x = dp(20)
        snackbar.snackbar_y = dp(20)
        snackbar.size_hint = None, None
        snackbar.width = Window.width - (dp(20) * 2) if Window.width < len(text) * 7 + dp(20) * 4 else len(text) * 7 + dp(20) * 2
        snackbar.height = dp(40)
        snackbar.pos_hint = {'center_x': 0.5}

        snackbar.radius = [8, 8, 8, 8]
        snackbar.elevation = 1
        snackbar.ids.text_bar.halign = 'center'
        snackbar.open()

    def PreCache(self):
        Cache.register('preload', limit=2)
        self.dialogEnterString.PreCache()
        self.dialogConfirm.PreCache()


rezkerApp = RezkerApp()
