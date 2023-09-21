import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

from libs.Controllers.downloads import DownloadsController
from libs.Controllers.item import ItemController
from libs.Controllers.library import LibraryController
from libs.Controllers.menu import MenuController


class MScreenManager(MDScreenManager):
    app = ObjectProperty()
    root_screen = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RootScreen(MDScreen):

    controller = ObjectProperty()
    model = ObjectProperty()

    screenManager = ObjectProperty(None)

    menuModel = ObjectProperty(None)
    menuController = ObjectProperty(None)
    menuScreen = ObjectProperty(None)

    libraryModel = ObjectProperty(None)
    libraryController = ObjectProperty(None)
    libraryScreen = ObjectProperty(None)

    downloadsModel = ObjectProperty(None)
    downloadsController = ObjectProperty(None)
    downloadsScreen = ObjectProperty(None)

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)

        self.app = app

        self.screenManager = MScreenManager(app=self.app, root_screen=self)

        self.libraryController = LibraryController(app=self.app, name='library')
        self.libraryScreen = self.libraryController.get_screen()
        self.library = {'model': self.libraryController.model, 'controller': self.libraryController, 'screen': self.libraryScreen}

        self.downloadsController = DownloadsController(app=self.app, name='downloads')
        self.downloadsScreen = self.downloadsController.get_screen()
        self.downloads = {'model': self.downloadsController.model, 'controller': self.downloadsController, 'screen': self.downloadsScreen}

        self.itemController = ItemController(app=self.app, name='item')
        self.itemScreen = self.itemController.get_screen()
        self.item = {'model': self.itemController.model, 'controller': self.itemController, 'screen': self.itemScreen}

        self.screens = {'library': self.library, 'downloads': self.downloads, 'item': self.item}

        self.screenManager.add_widget(self.libraryScreen)
        self.screenManager.add_widget(self.downloadsScreen)
        self.screenManager.add_widget(self.itemScreen)
        self.screenManager.add_widget(self.app.settingsScreen)

        self.menuController = MenuController(app=self.app)
        self.menuView = self.menuController.get_screen()

        self.ids.rootBox.add_widget(self.menuView)
        self.ids.rootBox.add_widget(self.screenManager)


Builder.load_file(os.path.join(os.path.dirname(__file__), "rootScreen.kv"))
