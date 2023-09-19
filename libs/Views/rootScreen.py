import os

from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.material_resources import dp
from kivymd.uix.behaviors import HoverBehavior, ScaleBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.spinner import MDSpinner

from libs.Controllers.downloads import DownloadsController
from libs.Controllers.item import ItemController
from libs.Controllers.library import LibraryController
from libs.Controllers.menu import MenuController


class HoverMDIconButton(MDIconButton, HoverBehavior):
    pass


class HoverMDFlatButton(MDFlatButton, HoverBehavior):
    pass


class HoverMDRaisedButton(MDRaisedButton, HoverBehavior):
    pass


class HoverMDBoxLayout(MDBoxLayout, HoverBehavior):
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

        self.screenManager = MDScreenManager()

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

        self.menuController = MenuController(app=self.app)
        self.menuView = self.menuController.get_screen()

        self.ids.rootBox.add_widget(self.menuView)
        self.ids.rootBox.add_widget(self.screenManager)


Builder.load_file(os.path.join(os.path.dirname(__file__), "rootScreen.kv"))
