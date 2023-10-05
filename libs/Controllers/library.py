from copy import copy

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.widget import Widget

from libs.Models.library import LibraryModel
from libs.Views.library import LibraryScreen


class LibraryController:

    def __init__(self, app, name):
        self.app = app
        self.model = LibraryModel()
        self.view = LibraryScreen(controller=self, model=self.model, name=name)

    def get_screen(self):
        return self.view

    def add_item(self, itemBaseInformation: dict):
        itemBaseInformation['controller'] = self
        itemBaseInformation['model'] = self.model
        self.model.add_item(itemBaseInformation)

    def openItem(self, link):
        self.app.rootScreen.openItem(link)
