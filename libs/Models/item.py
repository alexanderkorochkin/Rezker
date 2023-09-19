from kivy.clock import mainthread
from kivy.loader import Loader


class ItemModel:

    def __init__(self):
        self._observers = []
        self._itemBaseInformation = {}
        self._itemLinks = {}

    @property
    def itemBaseInformation(self):
        return self._itemBaseInformation

    @itemBaseInformation.setter
    def itemBaseInformation(self, data: dict):
        self._itemBaseInformation = data
        self.notify_observers()

    @property
    def itemLinks(self):
        return self._itemLinks

    @itemLinks.setter
    def itemLinks(self, data: dict):
        self._itemLinks = data
        self.notify_observers()

    def clearData(self):
        self._itemBaseInformation['url'] = ''
        self._itemBaseInformation['id'] = ''
        self._itemBaseInformation['thumbnail'] = 'assets/img/loading-image.png'
        self._itemBaseInformation['title'] = ''
        self._itemBaseInformation['title_en'] = ''
        self._itemBaseInformation['date'] = ''
        self._itemBaseInformation['type'] = ''
        self._itemBaseInformation['sub_type'] = ''
        self._itemBaseInformation['rate'] = ''
        self._itemBaseInformation['genre'] = ''
        self._itemBaseInformation['tagline'] = ''
        self._itemBaseInformation['age'] = ''
        self._itemBaseInformation['duration'] = ''
        self._itemBaseInformation['description'] = ''
        self.notify_observers()

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    @mainthread
    def notify_observers(self, what='all'):
        for x in self._observers:
            x.model_is_changed(what)
