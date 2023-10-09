import os
import re
import subprocess

import multitasking

from libs.Common.utils import getItemDataFromURL, dialogEnterFile, dialogEnterDir, addTags
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

    def removeFromLibrary(self):
        self.app.dialogConfirm.Open(
            title=f'Удалить {self.model.itemBaseInformation["title"]} из библиотеки?',
            confirm_text='Удалить',
            cancel_text='Отмена',
            confirm_action=self.app.rootScreen.libraryController.removeFromLibrary,
            arguments=(self.model.itemBaseInformation['url'],)
        )

    @multitasking.task
    def addToLibrary(self):
        if self.model.itemBaseInformation['type'] == 'movie':
            dialogEnterFile(self.addToLibraryLow)
        else:
            dialogEnterDir(self.addToLibraryLow)

    @multitasking.task
    def addToLibraryLow(self, fullpath):
        if fullpath:
            self.app.spinner.start(self.app.rootScreen)
            self.model.itemBaseInformation['fullpath'] = fullpath[0]
            if 'translation' not in self.model.itemBaseInformation:
                self.model.itemBaseInformation['translation'] = 'UNKNOWN'
            if 'quality' not in self.model.itemBaseInformation:
                self.model.itemBaseInformation['quality'] = 'UNKNOWN'
            if self.model.itemBaseInformation['type'] == 'movie':
                addTags(self.app, self.model.itemBaseInformation)
            else:
                for filename in os.listdir(fullpath[0]):
                    f = os.path.join(fullpath[0], filename)
                    if os.path.isfile(f):
                        try:
                            m = re.search('\[S(\d+)E(\d+)\]', filename)
                            season = int(m.group(1))
                            episode = int(m.group(2))
                            temp = self.model.itemBaseInformation.copy()
                            temp['season'] = season
                            temp['episode'] = episode
                            temp['fullpath'] = f
                            addTags(self.app, temp)
                        except Exception as e:
                            print(f"Can't detect season and episode in filename: {filename}. Skip tagging...")
            self.app.rootScreen.libraryController.addToLibrary(self.model.itemBaseInformation, fromItem=True)

    def addDownload(self, translation):
        self.app.spinner.start(self.app.rootScreen, timeout=None)
        itemBaseInformation = self.model.itemBaseInformation.copy()
        itemBaseInformation['translation'] = translation
        self.app.rootScreen.downloadsController.addDownload(itemBaseInformation, translation)

    @multitasking.task
    def RetryDownload(self, url, translation):
        self.app.rootScreen.downloadsController.addDownload(getItemDataFromURL(url).copy(), translation)

    def Reload(self, clear=False):
        if clear:
            self.PrepareData(self.model.itemBaseInformation['url'], itemBaseInformation=None, clear=True)
        else:
            self.PrepareData(self.model.itemBaseInformation['url'], itemBaseInformation=self.model.itemBaseInformation, clear=False)

    @multitasking.task
    def PrepareData(self, url, itemBaseInformation: dict = None, clear=False):
        if self.model.itemBaseInformation != {}:
            if url != self.model.itemBaseInformation['url'] or clear:
                self.model.clearData()
        if self.app.rootScreen.libraryController.isLibrary(url):
            itemBaseInformation = self.app.rootScreen.libraryController.getItemInfo(url)
            itemBaseInformation['isLibrary'] = True
            itemBaseInformation['isDownloading'] = False
            itemBaseInformation['translations'] = {}
        if self.app.rootScreen.downloadsController.isDownloading(url):
            itemBaseInformation = getItemDataFromURL(url)
            itemBaseInformation['isDownloading'] = True
            itemBaseInformation['isLibrary'] = False
        if itemBaseInformation is None:
            itemBaseInformation = getItemDataFromURL(url)
            itemBaseInformation['isLibrary'] = False
            itemBaseInformation['isDownloading'] = False
        else:
            if self.app.rootScreen.libraryController.isLibrary(url):
                itemBaseInformation = self.app.rootScreen.libraryController.getItemInfo(url)
                itemBaseInformation['isLibrary'] = True
                itemBaseInformation['isDownloading'] = False
            else:
                itemBaseInformation['isLibrary'] = False
        if itemBaseInformation:
            self.model.itemBaseInformation = itemBaseInformation.copy()
        self.last_item = url

