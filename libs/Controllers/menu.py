import validators
from kivy.uix.screenmanager import NoTransition

from libs.Models.menu import MenuModel
from libs.Views.menu import MenuView


class MenuController:

    def __init__(self, app):
        self.app = app
        self.model = MenuModel()
        self.view = MenuView(app=self.app, controller=self, model=self.model)
        self.loadSpinner = None

        self.last_request = ''

    def get_screen(self):
        return self.view

    def search(self, request):
        # self.app.rootScreen.screens['library']['controller'].add_item({'title': 'FUCK YOURSELF', 'cover': 'https://static.hdrezka.ac/i/2013/11/30/u5282eb49ebc3sd19f40y.jpg'})
        if validators.url(request):
            self.set_screen('item')
            if self.last_request != request:
                self.app.rootScreen.itemController.getItemDataFromURL(request)
        else:
            pass
        self.last_request = request

    def set_screen(self, screen_name):
        self.app.rootScreen.screenManager.transition = NoTransition()
        self.app.rootScreen.screenManager.current = screen_name
        self.model.current_screen = screen_name
