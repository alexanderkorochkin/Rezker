from libs.Views.menu import MenuView


class MenuController:

    def __init__(self, app, model, screen_manager):
        self.app = app
        self.model = model
        self.screen_manager = screen_manager
        self.view = MenuView(app=self.app, controller=self, model=self.model)

    def get_screen(self):
        return self.view

    def search(self, request):
        self.app.rootScreen.screens['library']['controller'].add_item({'title': 'FUCK YOURSELF', 'cover': 'https://static.hdrezka.ac/i/2013/11/30/u5282eb49ebc3sd19f40y.jpg'})
        # self.set_screen('item')

    def set_screen(self, screen_name):
        if screen_name == 'library':
            self.screen_manager.transition.direction = 'right'
        elif screen_name == 'downloads':
            self.screen_manager.transition.direction = 'left'
        self.screen_manager.current = screen_name
        self.model.current_screen = screen_name
