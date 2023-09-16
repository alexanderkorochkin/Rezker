from libs.Views.item import ItemScreen


class ItemController:

    def __init__(self, app, model, name):
        self.app = app
        self.model = model
        self.view = ItemScreen(controller=self, model=self.model, name=name)

    def get_screen(self):
        return self.view
