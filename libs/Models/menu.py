from kivy.clock import mainthread


class MenuModel:

    def __init__(self):
        self._observers = []
        self._history = [['library', None]]
        self._shift: int = 0

    @property
    def shift(self):
        return self._shift

    @shift.setter
    def shift(self, value: int):
        self._shift = value
        self.notify_observers()

    @property
    def current_screen(self):
        return self._history[-(self.shift + 1)]

    @property
    def last_screen(self):
        if self.shift >= len(self._history) - 1:
            return None
        return self._history[-(self.shift + 2)]

    @property
    def next_screen(self):
        if self.shift == 0:
            return None
        return self._history[-self.shift]

    def to_back_screen(self):
        if self.shift < len(self._history) - 1:
            self.shift = self.shift + 1
        return self.current_screen

    def to_next_screen(self):
        if self.shift > 0:
            self.shift = self.shift - 1
        return self.current_screen

    def set_screen(self, screen_name: str, request: str = None):
        if self.shift != 0:
            self._history = self._history[:-self.shift]
        self._history.append([screen_name, request])
        self.shift = 0
        if len(self._history) > 100:
            self._history = self._history[-100:]

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    @mainthread
    def notify_observers(self):
        for x in self._observers:
            x.model_is_changed()
