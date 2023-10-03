from kivy.clock import mainthread


class LibraryModel:

    def __init__(self):
        self._data = []
        self._observers = []
        self.controller = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: list):
        self._data = value
        self.notify_observers()

    def add_item(self, itemBaseInformation: dict):
        self._data.append(itemBaseInformation.copy())
        self.notify_observers()

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    @mainthread
    def notify_observers(self):
        for x in self._observers:
            x.model_is_changed()
