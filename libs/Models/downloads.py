import copy
import os

from kivy.clock import mainthread, Clock
from kivy.properties import partial
from pySmartDL import SmartDL
from pySmartDL.control_thread import ControlThread


class DownloadsModel:

    def __init__(self, app, controller):
        self.app = app
        self.controller = controller
        self._observers = []
        self.data = []
        self.downloaders = []
        self.download_orders = []


        self.startTask = None
        Clock.schedule_interval(self.check_orders, 2)

        self.updaterProgress = 'None'

    def check_orders(self, *args):
        count_active_downloaders = 0
        for downloader in self.downloaders:
            if downloader[1].get_status() == 'downloading':
                count_active_downloaders += 1
            elif downloader[1].get_status() == 'finished':
                self.controller.removeDownload(downloader[0])

        if count_active_downloaders < 1 and len(self.download_orders) > 0:
            key = self.download_orders[0][0]
            if not self.startTask and self.downloaders[self.getDownloaderIndexByID(key)][1].get_status() == 'ready':
                self.remove_order(key)
                self.startTask = Clock.schedule_once(partial(self.startDownload, key), 1)

    def remove_order(self, key: str):
        i = -1
        for order in self.download_orders:
            i += 1
            if order[0] == key:
                self.download_orders.pop(i)
                break

    def add_order(self, key: str, obj):
        self.download_orders.append([key, obj])

    def getDownloaderIndexByID(self, hdrezka_id: str):
        index = -1
        for item in self.downloaders:
            index += 1
            if str(item[0]) == str(hdrezka_id):
                return index
        return -1

    def getDataIndexByID(self, hdrezka_id: str):
        index = -1
        for item in self.data:
            index += 1
            if item['hdrezka_id'] == hdrezka_id:
                return index
        return -1

    def doUpdateProgress(self, *args):
        if len(self.downloaders) > 0 and len(self.data) > 0:
            if self.updaterProgress == 'None':
                self.updaterProgress = Clock.schedule_interval(self.updateProgress, 1)
        else:
            if self.updaterProgress != 'None':
                self.updaterProgress.cancel()
                self.updaterProgress = 'None'

    def updateProgress(self, *args):
        for i in range(len(self.downloaders)):
            try:
                downloader = self.downloaders[i][1]
                self.data[i]['speed'] = downloader.get_speed(human=True)
                self.data[i]['remaining_time'] = downloader.get_eta(human=True)
                self.data[i]['progress'] = round(downloader.get_progress() * 100, 2)
            except Exception:
                pass
        self.notify_observers()

    def startDownload(self, hdrezka_id: str, *args):
        self.downloaders[self.getDownloaderIndexByID(hdrezka_id)][1].start(blocking=False)
        self.data[self.getDataIndexByID(hdrezka_id)]['isStarted'] = True
        self.data[self.getDataIndexByID(hdrezka_id)]['isPaused'] = False
        Clock.schedule_once(self.doUpdateProgress)
        self.notify_observers()
        self.startTask = None

    def ppDownload(self, hdrezka_id: str):
        if self.data[self.getDataIndexByID(hdrezka_id)]['isPaused']:
            self.resumeDownload(hdrezka_id)
        else:
            self.pauseDownload(hdrezka_id)

    def resumeDownload(self, hdrezka_id: str):
        self.downloaders[self.getDownloaderIndexByID(hdrezka_id)][1].resume()
        self.data[self.getDataIndexByID(hdrezka_id)]['isPaused'] = False
        Clock.schedule_once(self.doUpdateProgress)
        self.notify_observers()

    def pauseDownload(self, hdrezka_id: str):
        self.downloaders[self.getDownloaderIndexByID(hdrezka_id)][1].pause()
        self.data[self.getDataIndexByID(hdrezka_id)]['isPaused'] = True
        Clock.schedule_once(self.doUpdateProgress)
        self.notify_observers()

    def removeDownload(self, hdrezka_id: str):
        if not self.downloaders[self.getDownloaderIndexByID(hdrezka_id)][1].isFinished():
            self.downloaders[self.getDownloaderIndexByID(hdrezka_id)][1].stop()
        self.downloaders.pop(self.getDownloaderIndexByID(hdrezka_id))
        self.data.pop(self.getDataIndexByID(hdrezka_id))
        Clock.schedule_once(self.doUpdateProgress)
        self.notify_observers()

    def addDownload(self, link, fullpath, info: dict):
        downloader = SmartDL(link, fullpath)
        self.downloaders.append([str(info['hdrezka_id']), downloader])
        temp = copy.deepcopy(info)
        temp['controller'] = self.controller
        temp['model'] = self
        temp['link'] = link
        temp['fullpath'] = fullpath
        temp['isPaused'] = False
        temp['isStarted'] = False
        temp['isFinished'] = False
        temp['progress'] = 0
        temp['speed'] = ''
        temp['remaining_time'] = ''
        self.data.append(temp)
        self.notify_observers()

        self.add_order(info['hdrezka_id'], downloader)

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    @mainthread
    def notify_observers(self, *args):
        for x in self._observers:
            x.model_is_changed()
