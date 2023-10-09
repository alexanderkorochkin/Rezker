import json
from copy import deepcopy

import multitasking
import requests
from kivy.clock import Clock

from libs.Models.library import LibraryModel
from libs.Views.library import LibraryScreen


class LibraryController:

    def __init__(self, app, name):
        self.app = app
        self.model = LibraryModel(self.app, self)
        self.view = LibraryScreen(controller=self, model=self.model, name=name)

        self.library_instance = {}

        self.libraryLoaded = False
        Clock.schedule_once(self.readLibraryTask, 1)

    def get_screen(self):
        return self.view

    def getItemInfo(self, url) -> dict:
        return self.library_instance[url]

    def isLibrary(self, url) -> bool:
        return url in list(self.library_instance.keys())

    def drawLibrary(self):
        self.model.data = list(self.library_instance.values())

    @multitasking.task
    def saveLibrary(self):
        try:
            tempOut = {}
            for key in list(self.library_instance.keys()):
                temp = self.library_instance[key].copy()
                temp['thumbnail'] = self.app.database.convertToRelative(temp['thumbnail'])
                temp['fullpath'] = self.app.database.convertToRelative(temp['fullpath'])
                tempOut[key] = temp
            with open(self.app.database.library_file, "w", encoding='utf8') as outfile:
                json.dump(tempOut, outfile, indent=4, separators=(',', ': '), ensure_ascii=False, skipkeys=True,
                          default=lambda o: '')
        except Exception as e:
            print(f"Unable to save lib file: {e}")

    def readLibraryTask(self, dt):
        self.readLibrary()

    @multitasking.task
    def readLibrary(self):
        try:
            with open(self.app.database.library_file, encoding='utf8') as json_file:
                temp = json.load(json_file)
            for key in list(temp.keys()):
                temp[key]['thumbnail'] = self.app.database.convertToDirect(temp[key]['thumbnail'])
                temp[key]['fullpath'] = self.app.database.convertToDirect(temp[key]['fullpath'])
            self.library_instance = temp.copy()
            self.model.data = list(self.library_instance.values())
            if not self.libraryLoaded:
                self.libraryLoaded = True
                self.app.spinner.stop()
        except Exception as e:
            if not self.libraryLoaded:
                self.libraryLoaded = True
                self.app.spinner.stop()
            print(f"Can't load library: {e}")

    def removeFromLibrary(self, url):
        self.library_instance.pop(url)
        self.saveLibrary()
        self.drawLibrary()
        if self.app.rootScreen.itemController.last_item == url:
            self.app.rootScreen.itemController.Reload(True)
        self.app.rootScreen.searchController.itemRemovedFromLibrary(url)

    def addToLibrary(self, downloadItem: dict, fromItem=False):
        if downloadItem['url'] not in self.library_instance:

            temp = downloadItem.copy()
            temp.pop('translations')
            if not fromItem:
                temp.pop('download_id')
                temp.pop('controller')
                if downloadItem['type'] != 'movie':
                    temp.pop('season')
                    temp.pop('episode')
                temp.pop('model')
                temp.pop('status')
                temp.pop('progress')
                temp.pop('speed')
                temp.pop('remaining_time')
                temp.pop('total_size')
                temp.pop('downloaded_size')
                temp.pop('downloader')
                temp.pop('doRemove')
                temp.pop('link')
            temp['controller'] = self
            temp['model'] = self.model
            temp['isLibrary'] = True
            # temp['isDownloading'] = False
            if str(temp['type']) != 'movie':
                temp['fullpath'] = '\\'.join(str(temp['fullpath']).split('\\')[:-1])

            url = temp['thumbnail']
            filepath = self.app.database.thumbnail_cache(f"{temp['hdrezka_id']}.png")
            try:
                data = requests.get(url)
                if data.status_code:
                    with open(filepath, "wb") as f:
                        f.write(data.content)
                    temp['thumbnail'] = filepath
                else:
                    raise Exception
            except Exception as e:
                print(f"Unable to cache thumbnail: {temp['hdrezka_id']} [{e}]")

            self.library_instance[temp['url']] = temp
            self.saveLibrary()
            self.drawLibrary()
            if self.app.rootScreen.itemController.last_item == temp['url']:
                self.app.rootScreen.itemController.Reload()
            self.app.rootScreen.searchController.itemAddedToLibrary(temp['url'])
        else:
            pass
        self.app.spinner.stop()

    def openItem(self, link):
        self.app.rootScreen.openItem(link)
