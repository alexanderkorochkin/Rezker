import json
import os

import multitasking
from kivy.clock import mainthread, Clock


class SettingsModel:

    def __init__(self):
        self._settings_data = {}
        self.view = None

    @multitasking.task
    def saveSettings(self):
        normal_data = {}
        for setting_key in list(self._settings_data.copy()):
            normal_data[setting_key] = self._settings_data[setting_key]['value']
        with open("settings.json", "w") as outfile:
            json.dump(normal_data, outfile, indent=4, separators=(',', ': '), skipkeys=True)

    def constructSettings(self):
        if os.path.exists('settings.json'):
            with open('settings.json') as json_file:
                try:
                    new_settings = json.load(json_file)
                except Exception:
                    new_settings = None
        else:
            new_settings = None

        try:
            with open('default_settings.json') as json_file:
                settings = json.load(json_file)
        except Exception:
            settings = None

        if settings is not None:
            for key in list(settings.keys()):
                try:
                    settings[key]['value'] = new_settings[key]
                except Exception:
                    pass
            self._settings_data = settings.copy()
            self.view.constructSettings(settings.copy())

    def set(self, key, value):
        self._settings_data[key]['value'] = value
        self.saveSettings()
        self.notify_observers()

    def get(self, key):
        return self._settings_data[key]['value']

    @mainthread
    def notify_observers(self):
        self.view.model_is_changed()
