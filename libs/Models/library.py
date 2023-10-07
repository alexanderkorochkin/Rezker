from kivy.clock import mainthread


class LibraryModel:

    def __init__(self, app, controller):
        self.app = app
        self._data = []
        self._observers = []
        self.controller = controller

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: list):
        self._data = value
        for item in self._data:
            item['controller'] = self.controller
            item['model'] = self
        self.notify_observers()

    def add_item(self, libraryItem: dict):
        self._data.append(libraryItem.copy())
        self.controller.saveLibrary()
        self.notify_observers()

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    @mainthread
    def notify_observers(self):
        for x in self._observers:
            x.model_is_changed()
