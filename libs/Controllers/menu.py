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
        if request == 'test':
            self.app.rootScreen.screens['library']['controller'].add_item({'title': 'FUCK YOURSELF',
                                                                           'thumbnail': 'https://static.hdrezka.ac/i/2013/11/30/u5282eb49ebc3sd19f40y.jpg',
                                                                           'url': 'https://hdrezkawer.org/films/fiction/2259-interstellar-2014.html'
                                                                           })
        self.view.set_cursor_to_start()
        if validators.url(request):
            self.set_screen('item')
            if self.last_request != request:
                self.app.rootScreen.itemController.getItemDataFromURL(request)
        else:
            pass
        self.last_request = request

    def screen_back(self):
        self.set_screen(self.model.last_screen, no_last=True)

    def set_screen(self, screen_name, no_last=False):
        if no_last:
            self.model.last_screen = ''
        else:
            self.model.last_screen = self.app.rootScreen.screenManager.current
        self.app.rootScreen.screenManager.transition = NoTransition()
        self.app.rootScreen.screenManager.current = screen_name
        self.model.current_screen = screen_name
