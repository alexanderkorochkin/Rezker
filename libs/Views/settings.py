import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen

from libs.Common.observer import Observer

from libs.Common.utils import str_to_class, dialogEnterDir


class SBool(MDBoxLayout):
    app = ObjectProperty()
    controller = ObjectProperty()
    type = StringProperty('SBool')
    key = StringProperty('')

    title = StringProperty('Title')
    sub_title = StringProperty('sub_title')
    value = BooleanProperty(False)

    def tap(self):
        self.controller.set(self.key, not self.value)


class SPath(MDBoxLayout):
    app = ObjectProperty()
    controller = ObjectProperty()
    type = StringProperty('SPath')
    key = StringProperty('')

    title = StringProperty('Title')
    sub_title = StringProperty('sub_title')
    value = StringProperty('value')

    def on_select_dir(self, *args):
        try:
            path = args[0][0]
            self.controller.set(self.key, path)
        except Exception:
            pass

    def tap(self):
        dialogEnterDir(self.on_select_dir)


class SNumeric(MDBoxLayout):
    app = ObjectProperty()
    controller = ObjectProperty()
    type = StringProperty('SNumeric')
    validate_type = StringProperty('sfloat')
    key = StringProperty('')

    title = StringProperty('Title')
    sub_title = StringProperty('sub_title')
    value = NumericProperty(0)

    def on_validate_value(self, text):
        self.controller.set(self.key, text)

    def tap(self):
        self.app.dialogEnterString.Open(validate_type=self.validate_type,
                                        title=self.title,
                                        confirm_action=self.on_validate_value,
                                        text=str(self.value))


class SString(MDBoxLayout):
    app = ObjectProperty()
    controller = ObjectProperty()
    type = StringProperty('SString')
    key = StringProperty('')

    title = StringProperty('Title')
    sub_title = StringProperty('sub_title')
    value = StringProperty('value')

    def on_validate_value(self, text):
        self.controller.set(self.key, str(text))

    def tap(self):
        self.app.dialogEnterString.Open(title=self.title,
                                        confirm_action=self.on_validate_value,
                                        text=str(self.value))


class SettingsScreen(MDScreen, Observer):
    app = ObjectProperty()
    controller = ObjectProperty()
    model = ObjectProperty()

    settings_dict = {}

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.view = self

    def constructSettings(self, settings_data: dict):
        data = settings_data.copy()
        for item_key in list(data.keys()):
            data[item_key]['controller'] = self.controller
            data[item_key]['app'] = self.app
            data[item_key]['key'] = item_key
            setting = str_to_class(__name__, data[item_key]['type'])(**data[item_key])
            self.settings_dict[item_key] = setting
            self.ids.all.add_widget(setting)

    def updateSetting(self, key, value):
        self.settings_dict[key].value = value


Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/settings.kv"))
