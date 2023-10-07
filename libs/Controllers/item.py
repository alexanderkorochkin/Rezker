import subprocess

import multitasking

from libs.Common.utils import getItemDataFromURL, dialogEnterFile, dialogEnterDir
from libs.Models.item import ItemModel
from libs.Views.item import ItemScreen

multitasking.set_max_threads(multitasking.config["CPU_CORES"] * 5)


class ItemController:

    def __init__(self, app, name):
        self.app = app
        self.model = ItemModel()
        self.view = ItemScreen(controller=self, model=self.model, name=name)
        self.last_item = None

    def get_screen(self):
        return self.view

    def chooseTranslation(self, translation):
        self.model.translation = translation

    def playItem(self):
        subprocess.Popen(rf'explorer /open,"{self.model.itemBaseInformation["fullpath"]}"')

    def addLibrary(self):
        if self.model.itemBaseInformation['type'] == 'movie':
            dialogEnterFile(self.addLibraryLow)
        else:
            dialogEnterDir(self.addLibraryLow)

    def addLibraryLow(self, fullpath):
        self.model.itemBaseInformation['fullpath'] = fullpath[0]
        self.model.itemBaseInformation['translation'] = 'UNKNOWN'
        self.model.itemBaseInformation['quality'] = 'UNKNOWN'
        self.app.rootScreen.libraryController.addToLibrary(self.model.itemBaseInformation, fromItem=True)

    def addDownload(self, translation):
        itemBaseInformation = self.model.itemBaseInformation.copy()
        itemBaseInformation['translation'] = translation
        self.app.rootScreen.downloadsController.addDownload(itemBaseInformation, translation)

    @multitasking.task
    def RetryDownload(self, url, translation):
        self.app.rootScreen.downloadsController.addDownload(getItemDataFromURL(url).copy(), translation)

    def Reload(self):
        self.PrepareData(self.model.itemBaseInformation['url'], self.model.itemBaseInformation)

    @multitasking.task
    def PrepareData(self, url, itemBaseInformation: dict = None):
        if self.model.itemBaseInformation != {}:
            if url != self.model.itemBaseInformation['url']:
                self.model.clearData()
        if self.app.rootScreen.libraryController.isLibrary(url):
            itemBaseInformation = self.app.rootScreen.libraryController.getItemInfo(url)
            itemBaseInformation['isLibrary'] = True
            itemBaseInformation['translations'] = {}
        if itemBaseInformation is None:
            itemBaseInformation = getItemDataFromURL(url)
        else:
            if self.app.rootScreen.libraryController.isLibrary(url):
                itemBaseInformation = self.app.rootScreen.libraryController.getItemInfo(url)
                itemBaseInformation['isLibrary'] = True
            else:
                itemBaseInformation['isLibrary'] = False
        if itemBaseInformation:
            self.model.itemBaseInformation = itemBaseInformation.copy()
        self.last_item = url

