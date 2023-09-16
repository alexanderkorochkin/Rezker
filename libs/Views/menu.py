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

    def model_is_changed(self):
        if self.model.current_screen == 'library':
            self.ids.btn_library.text_color = self.app.theme_cls.primary_color
            self.ids.btn_downloads.text_color = self.app.theme_cls.accent_color
        elif self.model.current_screen == 'downloads':
            self.ids.btn_library.text_color = self.app.theme_cls.accent_color
            self.ids.btn_downloads.text_color = self.app.theme_cls.primary_color


Builder.load_file(os.path.join(os.path.dirname(__file__), "menu.kv"))
