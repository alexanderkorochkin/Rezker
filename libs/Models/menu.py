from kivy.clock import mainthread


class MenuModel:

    def __init__(self):
        self._observers = []
        self._current_screen = 'library'
        self._last_screen = ''

    @property
    def current_screen(self):
        return self._current_screen

    @current_screen.setter
    def current_screen(self, value):
        self._current_screen = value
        self.notify_observers('current_screen')

    @property
    def last_screen(self):
        return self._last_screen

    @last_screen.setter
    def last_screen(self, value):
        self._last_screen = value
        self.notify_observers('last_screen')

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    @mainthread
    def notify_observers(self, key='all'):
        for x in self._observers:
            x.model_is_changed(key)
