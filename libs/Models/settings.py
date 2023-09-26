from kivy.clock import mainthread


class SettingsModel:

    def __init__(self):
        self._settings_data = {}
        self._observers = []

    def set(self, key, value):
        self._settings_data[key] = value
        self.notify_observers()

    def get(self, key):
        return self._settings_data[key]

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    @mainthread
    def notify_observers(self):
        for x in self._observers:
            x.model_is_changed()
