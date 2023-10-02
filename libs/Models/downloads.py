import copy
import os

import multitasking
from kivy import Logger
from kivy.clock import mainthread, Clock
from kivy.properties import partial
from pySmartDL import SmartDL
from pySmartDL.control_thread import ControlThread


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
        self.countDownloading = 0
        self.isClosing = False

    def logic(self, *args):
        if not self.isClosing:
            if len(self.data) > 0:
                for download_id in list(self.dictionary.keys()):
                    if self.isAlreadyDownloading(download_id):

                        downloader = self.getDataItemDownloader(download_id)
                        item = self.getDataItem(download_id)

                        if item['doRemove']:
                            self.removeDownload(download_id)
                            break
                        else:
                            if downloader.get_status() == 'finished':
                                item['status'] = STATUS.FINISHED
                                self.removeDownload(download_id)
                            elif downloader.get_status() == 'downloading':
                                item['status'] = STATUS.DOWNLOADING
                                item['progress'] = round(downloader.get_progress() * 100, 2)
                                item['speed'] = str(downloader.get_speed(human=True))
                                item['remaining_time'] = str(downloader.get_eta(human=True)) if str(downloader.get_eta(human=True)) != '0 seconds' else '∞'
                                item['total_size'] = str(downloader.get_final_filesize(human=True))
                                item['downloaded_size'] = str(downloader.get_dl_size(human=True))
                            elif downloader.get_status() == 'ready':
                                item['status'] = STATUS.READY
                                if self.countDownloading < self.app.msettings.get('MAX_ACTIVE_DOWNLOADS'):
                                    self.startDownload(download_id)
                            elif downloader.get_status() == 'paused':
                                item['status'] = STATUS.PAUSED
                            elif downloader.get_status() == 'combining':
                                item['status'] = STATUS.COMBINING
                            else:
                                Logger.warning(f"Catch error: {item['title']}")
                                item['status'] = STATUS.ERROR

                Clock.schedule_once(self.notify_observers)

    def startDownload(self, download_id: str, *args):
        self.getDataItemDownloader(download_id).start(blocking=False)
        self.getDataItem(download_id)['status'] = STATUS.DOWNLOADING
        self.countDownloading += 1
        self.notify_observers()

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
            Clock.schedule_once(partial(self.clearCache, file), 1)
        self.removeDataItem(download_id)
        self.countDownloading -= 1

    def addDownload(self, link, fullpath, itemBaseInformation: dict, season=None, episode=None):
        downloadInfo = itemBaseInformation.copy()
        if season and episode:
            downloadInfo['download_id'] = f"{downloadInfo['hdrezka_id']}.{season}.{episode}"
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
        downloadInfo['downloader'] = SmartDL(link, fullpath)
        downloadInfo['doRemove'] = False

        self.addDataItem(downloadInfo.copy(), downloadInfo['download_id'])

    def isAlreadyDownloading(self, download_id: str) -> bool:
        if download_id in list(self.dictionary.keys()):
            return True
        else:
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
    def clearCache(self, file, *args):
        i = 0
        while os.path.exists(str(file + f'.{i:03}')):
            try:
                os.remove(str(file + f'.{i:03}'))
            except Exception:
                print(f"Unable to remove file: {str(file + f'.{i:03}')}.")
            i += 1

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
