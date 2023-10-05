import os

import multitasking

from libs.Common.utils import remove_not_valid_chars
from libs.Models.downloads import DownloadsModel
from libs.Views.downloads import DownloadsScreen
from libs.hdrezkalib.hdrezka import HdRezkaApi


class DownloadsController:

    def __init__(self, app, name):
        self.app = app
        self.model = DownloadsModel(self.app, self)
        self.view = DownloadsScreen(controller=self, model=self.model, name=name)

    def get_screen(self):
        return self.view

    def open_item(self, link):
        self.app.rootScreen.menuController.search(link)

    def on_close(self):
        self.model.on_close()

    @multitasking.task
    def ppDownload(self, download_id: str):
        self.model.ppDownload(download_id)

    @multitasking.task
    def removeDownload(self, download_id: str):
        self.model.setDoRemoveDownload(download_id)

    @multitasking.task
    def addDownload(self, itemBaseInformation: dict, translation):

        item = HdRezkaApi(itemBaseInformation['url'])

        if item.type == 'movie':
            try:
                stream = item.getStream(translation=str(translation))
                link = stream(list(stream.videos.keys())[self.app.msettings.get('debug_quality')])  # Quality = -1 - MAX
                title = item.title + f" ({item.date.split(' ')[-2]})"
                path = os.path.abspath(self.app.msettings.get('downloads_destination'))
                normalName = remove_not_valid_chars(title, '\/:*?"<>|').replace(' .', '.')
                file_extension = link.split('.')[-1]
                fullpath = os.path.join(path, normalName + f'.{file_extension}')
                self.model.addDownload(link, fullpath, itemBaseInformation.copy())
            except Exception:
                print(f"Downloads.Controller: Error while trying to get info of film: {itemBaseInformation['title']}")
        else:
            for season in list(item.seriesInfo[str(translation)]['seasons'].keys()):
                for episode in item.seriesInfo[str(translation)]['episodes'][season]:
                    try:
                        stream = item.getStream(str(season), str(episode), str(translation))
                        link = stream(list(stream.videos.keys())[self.app.msettings.get('debug_quality')])  # Quality = -1 - MAX
                        title = item.title + f" ({item.date.split(' ')[-2]})"
                        path = os.path.abspath(self.app.msettings.get('downloads_destination'))
                        normalName = remove_not_valid_chars(title, '\/:*?"<>|').replace(' .', '.')
                        clearName = normalName
                        file_extension = link.split('.')[-1]
                        normalName = normalName + f' [S{season}E{episode}]'
                        path = os.path.join(path, clearName)
                        fullpath = os.path.join(path, normalName + f'.{file_extension}')
                        self.model.addDownload(link, fullpath, itemBaseInformation.copy(), season=season, episode=episode)
                    except Exception:
                        print(f"Downloads.Controller: Error while trying to get info of series: {itemBaseInformation['title']}, S{season}E{episode}")
