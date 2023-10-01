from libs.Models.settings import SettingsModel
from libs.Views.settings import SettingsScreen


class SettingsController:

    def __init__(self, app, name):
        self.app = app
        self.model = SettingsModel()
        self.view = SettingsScreen(controller=self, model=self.model, name=name)

        # Default Settings
        self.model.set('downloads_destination', 'C:\HDRezker')
        self.model.set('library_destination', 'C:\HDRezker')

    def get_screen(self):
        return self.view

    def get(self, key):
        return self.model.get(key)

    def set(self, key, value):
        self.model.set(key, value)
