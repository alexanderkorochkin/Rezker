from kivy.clock import mainthread


class ItemModel:

    def __init__(self):
        self._observers = []
        self._itemBaseInformation = {}
        self._activeTranslation = ''

    @property
    def itemBaseInformation(self):
        return self._itemBaseInformation

    @itemBaseInformation.setter
    def itemBaseInformation(self, data: dict):
        self._itemBaseInformation = data
        self._itemBaseInformation['year'] = str(self._itemBaseInformation['date'].split(' ')[-2])
        self.notify_observers('itemBaseInformation')

    @property
    def activeTranslation(self):
        return self._activeTranslation

    @activeTranslation.setter
    def activeTranslation(self, value):
        self._activeTranslation = value
        self.notify_observers('activeTranslation')

    def clearData(self):
        self._itemBaseInformation['url'] = ''
        self._itemBaseInformation['hdrezka_id'] = ''
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
        self._itemBaseInformation['translations'] = {}
        self._activeTranslation = ''
        self.notify_observers()

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    @mainthread
    def notify_observers(self, what='all'):
        for x in self._observers:
            x.model_is_changed(what)
