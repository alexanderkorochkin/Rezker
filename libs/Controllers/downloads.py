from libs.Views.downloads import DownloadsScreen


class DownloadsController:

    def __init__(self, app, model, name):
        self.app = app
        self.model = model
        self.view = DownloadsScreen(controller=self, model=self.model, name=name)

    def get_screen(self):
        return self.view

    # def set_c(self, value):
    #     self.model.c = value
    #
    # def set_d(self, value):
    #     self.model.d = value
