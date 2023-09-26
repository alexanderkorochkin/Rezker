import os

import multitasking
from pySmartDL import SmartDL

from libs.Models.downloads import DownloadsModel
from libs.Views.downloads import DownloadsScreen
from libs.hdrezkalib.hdrezka import HdRezkaApi


def remove_not_valid(value, chars):
    for c in chars:
        value = value.replace(c, '.')
    return value


class DownloadsController:

    def __init__(self, app, name):
        self.app = app
        self.model = DownloadsModel(self.app, self)
        self.view = DownloadsScreen(controller=self, model=self.model, name=name)

    def get_screen(self):
        return self.view

    def open_item(self, link):
        self.app.rootScreen.menuController.search(link)

    @multitasking.task
    def ppDownload(self, hdrezka_id: str):
        self.model.ppDownload(hdrezka_id)

    @multitasking.task
    def resumeDownload(self, hdrezka_id: str):
        self.model.resumeDownload(hdrezka_id)

    @multitasking.task
    def pauseDownload(self, hdrezka_id: str):
        self.model.pauseDownload(hdrezka_id)

    @multitasking.task
    def removeDownload(self, hdrezka_id: str):
        self.model.removeDownload(hdrezka_id)

    @multitasking.task
    def addDownload(self, itemBaseInformation: dict, translation):

        if self.model.getDownloaderIndexByID(itemBaseInformation['hdrezka_id']) == -1:

            item = HdRezkaApi(itemBaseInformation['url'])

            if item.type == 'movie':
                stream = item.getStream(translation=str(translation))
                link = stream(list(stream.videos.keys())[0])  # Quality = -1 - MAX
                title = item.title + f" ({item.date.split(' ')[-2]})"
                path = os.path.abspath(self.app.msettings.get('downloads_destination'))
                normalName = remove_not_valid(title, '\/:*?"<>|').replace(' .', '.')
                file_extension = link.split('.')[-1]
                fullpath = os.path.join(path, normalName + f'.{file_extension}')
                self.model.addDownload(link, fullpath, itemBaseInformation.copy())
            else:
                for season in list(item.seriesInfo[str(translation)]['seasons'].keys()):
                    for episode in item.seriesInfo[str(translation)]['episodes'][season]:
                        stream = item.getStream(str(season), str(episode), str(translation))
                        link = stream(list(stream.videos.keys())[0])  # Quality = -1 - MAX
                        title = item.title + f" ({item.date.split(' ')[-2]})"
                        path = os.path.abspath(self.app.msettings.get('downloads_destination'))
                        normalName = remove_not_valid(title, '\/:*?"<>|').replace(' .', '.')
                        clearName = normalName
                        file_extension = link.split('.')[-1]
                        normalName = normalName + f' [S{season}E{episode}]'
                        path = os.path.join(path, clearName)
                        fullpath = os.path.join(path, normalName + f'.{file_extension}')
                        self.model.addDownload(link, fullpath, itemBaseInformation.copy())

        else:
            print('Already in downloads!')
