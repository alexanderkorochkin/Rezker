import os

from kivy.animation import Animation
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, partial
from kivy.uix.screenmanager import NoTransition
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.spinner import MDSpinner

from libs.Controllers.downloads import DownloadsController
from libs.Controllers.item import ItemController
from libs.Controllers.library import LibraryController
from libs.Controllers.menu import MenuController
from libs.Controllers.search import SearchController


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

        self.searchController = SearchController(app=self.app, name='search')
        self.searchScreen = self.searchController.get_screen()
        self.search = {'model': self.searchController.model, 'controller': self.searchController, 'screen': self.searchScreen}

        self.screens = {'library': self.library, 'downloads': self.downloads, 'item': self.item, 'search': self.search}

        self.screenManager.add_widget(self.libraryScreen)
        self.screenManager.add_widget(self.downloadsScreen)
        self.screenManager.add_widget(self.itemScreen)
        self.screenManager.add_widget(self.searchScreen)
        self.screenManager.add_widget(self.app.settingsScreen)

        self.menuController = MenuController(app=self.app)
        self.menuView = self.menuController.get_screen()

        self.ids.rootBox.add_widget(self.menuView)
        self.ids.rootBox.add_widget(self.screenManager)

    @mainthread
    def set_screen(self, screen_name, request=None, simple=False, *args):
        self.menuController.view.cancel_input_selection()
        if request and simple:
            if screen_name == 'search':
                self.openSearch(request, silent=simple)
            elif screen_name == 'item':
                self.openItem(request, silent=simple)
        self.screenManager.transition = NoTransition()
        self.screenManager.current = screen_name
        if not simple:
            self.menuController.model.set_screen(screen_name, request)

    def openSearch(self, request, silent=False):
        self.menuController.view.set_input_text(request)
        if request != self.searchController.last_request:
            self.searchController.model.clear_items()
            self.searchScreen.recycleList.scroll_y = 1
            self.searchController.Search(request)
        if silent:
            Clock.schedule_once(partial(self.set_screen, 'search', None, True), 0)
        else:
            Clock.schedule_once(partial(self.set_screen, 'search', request, False), 0)

    def openItem(self, url, itemBaseInformation: dict = None, silent=False):
        self.menuController.view.set_input_text(url)
        self.menuController.view.cancel_input_selection()
        if url != self.itemController.last_item:
            self.itemScreen.ids.scroll.scroll_y = 1
            self.itemController.PrepareData(url, itemBaseInformation)
        if silent:
            Clock.schedule_once(partial(self.set_screen, 'item', None, True), 0)
        else:
            Clock.schedule_once(partial(self.set_screen, 'item', url, False), 0)


Builder.load_file(os.path.join(os.path.dirname(__file__), "rootScreen.kv"))
