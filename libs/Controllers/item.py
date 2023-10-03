import multitasking

from libs.Common.utils import getItemDataFromURL
from libs.Models.item import ItemModel
from libs.Views.item import ItemScreen

multitasking.set_max_threads(multitasking.config["CPU_CORES"] * 5)


class ItemController:

    def __init__(self, app, name):
        self.app = app
        self.model = ItemModel()
        self.view = ItemScreen(controller=self, model=self.model, name=name)
        self.item = None

    def get_screen(self):
        return self.view

    def chooseTranslation(self, translation):
        self.model.activeTranslation = translation

    def addDownload(self, translation):
        self.app.rootScreen.downloadsController.addDownload(self.model.itemBaseInformation, translation)

    @multitasking.task
    def PrepareData(self, url, itemBaseInformation: dict = None):
        self.model.clearData()
        if itemBaseInformation is None:
            itemBaseInformation = getItemDataFromURL(url)
        if itemBaseInformation:
            self.model.itemBaseInformation = itemBaseInformation.copy()
