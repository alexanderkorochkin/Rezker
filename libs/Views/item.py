import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from libs.Common.observer import Observer


class ItemScreen(MDScreen, Observer):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)

    def model_is_changed(self):
        pass


Builder.load_file(os.path.join(os.path.dirname(__file__), "item.kv"))
