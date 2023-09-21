import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty
from kivymd.uix.boxlayout import MDBoxLayout


class MenuView(MDBoxLayout):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model.add_observer(self)
        self.app = app
        self.callbacks = {
            'current_screen': self.current_screen_callback,
            'last_screen': self.last_screen_callback
        }

    def set_cursor_to_start(self):
        self.ids.search_input.cursor = [0, 0]

    def current_screen_callback(self):
        if self.model.current_screen == 'library' or self.model.current_screen == 'downloads':
            self.ids.btn_screen_back.disabled = True

        self.ids.btn_library.text_color = self.app.theme_cls.primary_color if self.model.current_screen == 'library' else self.app.theme_cls.accent_color
        self.ids.btn_downloads.text_color = self.app.theme_cls.primary_color if self.model.current_screen == 'downloads' else self.app.theme_cls.accent_color
        self.ids.btn_settings.icon_color = self.app.theme_cls.primary_color if self.model.current_screen == 'settings' else 'white'
        self.ids.btn_search.icon_color = self.app.theme_cls.primary_color if self.model.current_screen == 'item' else 'white'

    def last_screen_callback(self):
        if self.model.current_screen != 'library' and self.model.current_screen != 'downloads':
            if self.model.last_screen:
                self.ids.btn_screen_back.disabled = False
            else:
                self.ids.btn_screen_back.disabled = True

    def model_is_changed(self, key='all'):
        for callback_key in self.callbacks.keys():
            if key == callback_key or key == 'all':
                self.callbacks[callback_key]()


Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/menu.kv"))
