import os

import multitasking
from kivy.clock import mainthread, Clock
from kivy.properties import partial
from pySmartDL import SmartDL

from libs.Common.utils import create_dir, addTags
from libs.Views.common import truncate_string


class STATUS:
    READY = 'Ready'
    DOWNLOADING = 'Downloading'
    FINISHED = 'Finished'
    PAUSED = 'Paused'
    ERROR = 'Error'
    COMBINING = 'Combining'


class DownloadsModel:

    def __init__(self, app, controller):
        self.app = app
        self.controller = controller
        self._observers = []
        self.data = []
        self.dictionary = {}
        self.updateTask = Clock.schedule_interval(self.logic, 1)
        self.downloading = []
        self.isClosing = False
        self.items_deleting = []
        self.logic_in_process = False

        self.max_active_downloads = 1

    def logic(self, *args):
        if not self.isClosing:
            self.logic_in_process = True
            if len(self.data) > 0:
                for download_id in list(self.dictionary.keys()):
                    if self.isAlreadyDownloading(download_id):

                        downloader = self.getDataItemDownloader(download_id)
                        item = self.getDataItem(download_id)

                        if item['doRemove']:
                            self.removeDownload(download_id)
                        else:
                            if downloader.get_status() == 'finished':
                                if downloader.isSuccessful():
                                    item['status'] = STATUS.FINISHED
                                    self.removeDownload(download_id)
                                else:
                                    print('FUCKFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
                                    print('FUCKFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
                                    print('FUCKFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
                                    print('FUCKFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
                                    print('FUCKFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
                                    item['status'] = STATUS.ERROR
                            elif downloader.get_status() == 'downloading':
                                item['status'] = STATUS.DOWNLOADING
                                item['progress'] = round(downloader.get_progress() * 100, 2)
                                item['speed'] = str(downloader.get_speed(human=True))
                                item['remaining_time'] = str(downloader.get_eta(human=True)) if str(downloader.get_eta(human=True)) != '0 seconds' else '∞'
                                item['total_size'] = str(downloader.get_final_filesize(human=True))
                                item['downloaded_size'] = str(downloader.get_dl_size(human=True))
                            elif downloader.get_status() == 'ready':
                                item['status'] = STATUS.READY
                                if len(self.downloading) < self.max_active_downloads:
                                    self.startDownload(download_id)
                            elif downloader.get_status() == 'paused':
                                item['status'] = STATUS.PAUSED
                            elif downloader.get_status() == 'combining':
                                item['status'] = STATUS.COMBINING
                            else:
                                print(f"Downloads.Model: Catch error: {item['title']}")
                                item['status'] = STATUS.ERROR
                Clock.schedule_once(self.notify_observers)
        self.logic_in_process = False

    def startDownload(self, download_id: str, *args):
        create_dir("\\".join(str(self.getDataItem(download_id)['fullpath']).split("\\")[:-1]))
        self.getDataItemDownloader(download_id).start(blocking=False)
        self.getDataItem(download_id)['status'] = STATUS.DOWNLOADING
        self.downloading.append(download_id)
        self.notify_observers()

    @property
    def UpdateInfo(self):
        active = len(self.downloading)
        if active == 0:
            return None
        else:
            item = self.getDataItem(self.downloading[0])
            if item['type'] == 'movie':
                return f"{item['status']}: {truncate_string(item['title'], 30)} ({item['year']}) -> {item['downloaded_size']}/{item['total_size']} [{item['progress']}%], {item['remaining_time']}"
            else:
                return f"{item['status']}: {truncate_string(item['title'], 30)} ({item['year']}) [S{item['season']}E{item['episode']}] -> {item['downloaded_size']}/{item['total_size']} [{item['progress']}%], {item['remaining_time']}"

    def ppDownload(self, download_id: str):
        if self.getDataItem(download_id)['status'] == STATUS.PAUSED:
            self.resumeDownload(download_id)
        else:
            self.pauseDownload(download_id)

    def resumeDownload(self, download_id: str):
        self.getDataItemDownloader(download_id).resume()
        self.getDataItem(download_id)['status'] = STATUS.DOWNLOADING
        self.notify_observers()

    def pauseDownload(self, download_id: str):
        self.getDataItemDownloader(download_id).pause()
        self.getDataItem(download_id)['status'] = STATUS.PAUSED
        self.notify_observers()

    def setDoRemoveDownload(self, download_id: str):
        self.getDataItem(download_id)['doRemove'] = True

    def removeDownload(self, download_id: str):
        if not self.getDataItemDownloader(download_id).isFinished():
            file = self.getDataItem(download_id)['fullpath']
            self.getDataItemDownloader(download_id).stop()
            isSeries = True if self.getDataItem(download_id)['type'] != 'movie' else False
            args = (file, isSeries)
            Clock.schedule_once(partial(self.clearCache, *args), 2)
        else:
            addTags(app=self.app, info=self.getDataItem(download_id).copy())
        if self.downloading.count(download_id) > 0:
            self.downloading.remove(download_id)
        self.removeDataItem(download_id)

    def addDownload(self, link, fullpath, downloadBaseInformation: dict, season=None, episode=None):
        downloadInfo = downloadBaseInformation.copy()
        if season and episode:
            downloadInfo['download_id'] = f"{downloadInfo['hdrezka_id']}.{season}.{episode}"
            downloadInfo['season'] = str(season)
            downloadInfo['episode'] = str(episode)
        else:
            downloadInfo['download_id'] = f"{downloadInfo['hdrezka_id']}"

        if self.isAlreadyDownloading(downloadInfo['download_id']):
            return

        downloadInfo['controller'] = self.controller
        downloadInfo['model'] = self
        downloadInfo['link'] = link
        downloadInfo['fullpath'] = fullpath
        downloadInfo['status'] = STATUS.READY
        downloadInfo['progress'] = 0
        downloadInfo['speed'] = '0'
        downloadInfo['remaining_time'] = '∞'
        downloadInfo['total_size'] = '0'
        downloadInfo['downloaded_size'] = '0'
        downloadInfo['downloader'] = SmartDL([link, link, link, link], fullpath)
        downloadInfo['doRemove'] = False

        self.addDataItem(downloadInfo.copy(), downloadInfo['download_id'])

    def isAlreadyDownloading(self, download_id: str) -> bool:
        if download_id in list(self.dictionary.keys()):
            return True
        else:
            return False

    def isThereItemWithHdrezkaID(self, hdrezka_id: str):
        for item in self.data:
            if item['hdrezka_id'] == hdrezka_id:
                return True
        return False

    def getDataItemDownloader(self, download_id: str) -> SmartDL:
        return self.getDataItem(download_id)['downloader']

    def getDataItem(self, download_id: str) -> dict:
        return self.data[self.idToIndex(download_id)]

    def removeDataItem(self, download_id: str):
        self.data.pop(self.idToIndex(download_id))
        doShift = False
        for key in list(self.dictionary.keys()):
            if doShift:
                self.dictionary[key] = self.dictionary[key] - 1
            if key == download_id:
                doShift = True
        self.dictionary.pop(download_id)
        self.notify_observers()

    def addDataItem(self, itemInfo: dict, download_id: str):
        self.data.append(itemInfo.copy())
        self.dictionary[download_id] = len(self.data) - 1
        self.notify_observers()

    def idToIndex(self, download_id: str):
        return self.dictionary[download_id]

    @multitasking.task
    def removeSeriesDir(self, directory, *args):
        try:
            os.rmdir(directory)
        except Exception:
            pass

    @multitasking.task
    def clearCache(self, file, isSeries=False, *args):
        i = 0
        while os.path.exists(str(file + f'.{i:03}')):
            try:
                os.remove(str(file + f'.{i:03}'))
            except Exception:
                print(f"clearCache: Unable to remove file: {str(file + f'.{i:03}')}.")
            i += 1
        if isSeries:
            folder = "\\".join(file.split("\\")[:-1])
            Clock.schedule_once(partial(self.removeSeriesDir, folder), 1)

    def on_close(self):
        self.isClosing = True
        self.updateTask.cancel()
        for download_id in list(self.dictionary.keys()):
            self.removeDownload(download_id)

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    @mainthread
    def notify_observers(self, *args):
        for x in self._observers:
            x.model_is_changed()
