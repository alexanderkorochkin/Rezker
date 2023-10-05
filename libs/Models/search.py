from kivy.clock import mainthread


class SearchModel:

    def __init__(self):
        self._data = []
        self._observers = []
        self.controller = None

    @property
    def data(self):
        return self._data

    def add_items(self, itemsBaseInformation: list, controller, model):
        for itemBaseInformation in itemsBaseInformation:
            itemBaseInformation['controller'] = controller
            itemBaseInformation['model'] = model
            self._data.append(itemBaseInformation.copy())
        self.notify_observers(len(self._data))

    def clear_items(self):
        if self._data:
            self._data.clear()
            self.notify_observers(0)

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    @mainthread
    def notify_observers(self, new_len):
        for x in self._observers:
            x.model_is_changed(new_len)
