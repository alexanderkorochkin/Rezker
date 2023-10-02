import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen

from libs.Common.observer import Observer
from libs.Views.common import str_to_class


class SBool(MDBoxLayout):
    app = ObjectProperty()
    controller = ObjectProperty()
    type = StringProperty('SBool')

    title = StringProperty('Title')
    sub_title = StringProperty('sub_title')
    value = BooleanProperty(False)


class SPath(MDBoxLayout):
    app = ObjectProperty()
    controller = ObjectProperty()
    type = StringProperty('SPath')

    title = StringProperty('Title')
    sub_title = StringProperty('sub_title')
    value = StringProperty('value')


class SNumeric(MDBoxLayout):
    app = ObjectProperty()
    controller = ObjectProperty()
    type = StringProperty('SNumeric')

    title = StringProperty('Title')
    sub_title = StringProperty('sub_title')
    value = NumericProperty(0)


class SString(MDBoxLayout):
    app = ObjectProperty()
    controller = ObjectProperty()
    type = StringProperty('SString')

    title = StringProperty('Title')
    sub_title = StringProperty('sub_title')
    value = StringProperty('value')


class SettingsScreen(MDScreen, Observer):
    app = ObjectProperty()
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.view = self

    def constructSettings(self, settings_data: dict):
        data = settings_data.copy()
        for item_key in list(data.keys()):
            data[item_key]['controller'] = self.controller
            data[item_key]['app'] = self.app
            setting = str_to_class(__name__, data[item_key]['type'])(**data[item_key])
            self.ids.all.add_widget(setting)

    def model_is_changed(self):
        pass


Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/settings.kv"))
