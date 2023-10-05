import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout


class MenuView(MDBoxLayout):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model.add_observer(self)
        self.app = app

    def set_cursor_to_start(self):
        self.ids.search_input.cursor = [0, 0]

    def set_input_text(self, text: str):
        self.ids.search_input.text = text

    def cancel_input_selection(self):
        self.ids.search_input.cancel_selection()

    def model_is_changed(self):
        if self.model.last_screen:
            self.ids.btn_screen_back.disabled = False
        else:
            self.ids.btn_screen_back.disabled = True

        if self.model.next_screen:
            self.ids.btn_screen_next.disabled = False
        else:
            self.ids.btn_screen_next.disabled = True

        self.ids.btn_library.text_color = self.app.theme_cls.primary_color if self.model.current_screen[0] == 'library' else self.app.theme_cls.accent_color
        self.ids.btn_downloads.text_color = self.app.theme_cls.primary_color if self.model.current_screen[0] == 'downloads' else self.app.theme_cls.accent_color
        self.ids.btn_settings.icon_color = self.app.theme_cls.primary_color if self.model.current_screen[0] == 'settings' else 'white'
        self.ids.btn_search.icon_color = self.app.theme_cls.primary_color if self.model.current_screen[0] == 'item' else 'white'


Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/menu.kv"))
