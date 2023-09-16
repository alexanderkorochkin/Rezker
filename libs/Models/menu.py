class MenuModel:

    def __init__(self):
        self._observers = []
        self._current_screen = 'library'

    @property
    def current_screen(self):
        return self._current_screen

    @current_screen.setter
    def current_screen(self, value):
        self._current_screen = value
        self.notify_observers()

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self):
        for x in self._observers:
            x.model_is_changed()
