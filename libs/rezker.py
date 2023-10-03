import os

from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.loader import Loader
from kivy.properties import NumericProperty, ObjectProperty
from kivymd.app import MDApp
from plyer import storagepath

from libs.Common.database import DataManager
from libs.Controllers.settings import SettingsController
from libs.Views.common import LDialogEnterString
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
        self.database = DataManager()
        self.title = "Rezker"
        self.rootScreen = None

        self.dialogEnterString = LDialogEnterString(app=self)

        self.msettings = SettingsController(app=self, name='settings')
        self.settingsScreen = self.msettings.get_screen()

    def provider(self, url: str = None):
        if url is not None:
            return url.replace('https://hdrezkawer.org', self.msettings.get('provider'))
        else:
            return self.msettings.get('provider')

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
            self.COLS_LIBRARY = 7

    def on_stop(self):
        self.rootScreen.downloadsController.on_close()

    def on_start(self):
        Config.set('graphics', 'resizable', True)
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

        return self.rootScreen

    def PreCache(self):
        self.dialogEnterString.PreCache()


rezkerApp = RezkerApp()
