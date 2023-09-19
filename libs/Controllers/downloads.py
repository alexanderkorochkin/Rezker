from libs.Models.downloads import DownloadsModel
from libs.Views.downloads import DownloadsScreen


class DownloadsController:

    def __init__(self, app, name):
        self.app = app
        self.model = DownloadsModel()
        self.view = DownloadsScreen(controller=self, model=self.model, name=name)

    def get_screen(self):
        return self.view
