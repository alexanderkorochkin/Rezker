from libs.Models.library import LibraryModel
from libs.Views.library import LibraryScreen


class LibraryController:

    def __init__(self, app, name):
        self.app = app
        self.model = LibraryModel()
        self.view = LibraryScreen(controller=self, model=self.model, name=name)

    def get_screen(self):
        return self.view

    def add_item(self, item: dict):
        self.model.add_item(item)
