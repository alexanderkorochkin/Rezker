from kivy.clock import mainthread


class ItemModel:

    def __init__(self):
        self._observers = []
        self._itemBaseInformation = {}
        self._translation = ''

    @property
    def itemBaseInformation(self):
        return self._itemBaseInformation

    @itemBaseInformation.setter
    def itemBaseInformation(self, data: dict):
        self._itemBaseInformation = data
        if self._itemBaseInformation['date'] != 'None' and self._itemBaseInformation['date'] != '':
            self._itemBaseInformation['year'] = str(self._itemBaseInformation['date'].split(' ')[-2])
        else:
            self._itemBaseInformation['year'] = self._itemBaseInformation['url'].split('/')[-1].split('.')[0].split('-')[-1]
            self._itemBaseInformation['date'] = self._itemBaseInformation['url'].split('/')[-1].split('.')[0].split('-')[-1] + ' год'
        self._itemBaseInformation['summary_info'] = ', '.join([self._itemBaseInformation['year'], self._itemBaseInformation['country'], self._itemBaseInformation['genre'].split(', ')[0]])
        self.notify_observers('itemBaseInformation')

    @property
    def translation(self):
        return self._translation

    @translation.setter
    def translation(self, value):
        self._translation = value
        self.notify_observers('translation')

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
        self._itemBaseInformation['fullpath'] = ''
        self._itemBaseInformation['isLibrary'] = False
        self._itemBaseInformation['translations'] = {}
        self._translation = ''
        self.notify_observers()

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    @mainthread
    def notify_observers(self, what='all'):
        for x in self._observers:
            x.model_is_changed(what)
