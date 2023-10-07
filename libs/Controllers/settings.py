import json
import os
import sys

import multitasking

from libs.Models.settings import SettingsModel
from libs.Views.settings import SettingsScreen


class SettingsController:

    def __init__(self, app, name):
        self.app = app
        self.model = SettingsModel()
        self.view = SettingsScreen(app=self.app, controller=self, model=self.model, name=name)
        self.constructSettings()

    def get_screen(self):
        return self.view

    @multitasking.task
    def saveSettings(self):
        normal_data = {}
        for setting_key in list(self.model.settings_data.keys()):
            normal_data[setting_key] = self.model.settings_data[setting_key]['value']
        with open(self.app.database.settings_file, "w") as outfile:
            json.dump(normal_data, outfile, indent=4, separators=(',', ': '), skipkeys=True)

    def constructSettings(self):
        if os.path.exists(self.app.database.settings_file):
            with open(self.app.database.settings_file) as json_file:
                try:
                    new_settings = json.load(json_file)
                except Exception:
                    new_settings = None
        else:
            new_settings = None

        try:
            if getattr(sys, 'frozen', False):
                with open(os.path.join(sys._MEIPASS,'default/default_settings.json')) as json_file:
                    settings = json.load(json_file)
            else:
                with open('default/default_settings.json') as json_file:
                    settings = json.load(json_file)
        except Exception:
            settings = None

        if settings is not None:
            for key in list(settings.keys()):
                try:
                    settings[key]['value'] = new_settings[key]
                except Exception:
                    pass
            self.model._settings_data = settings.copy()
            self.view.constructSettings(settings.copy())
        else:
            print('SETTINGS NOT CONSTRUCTED IN CONTROLLER!')

    def set(self, key, value):
        if self.checkValue(key, value):
            self.model.set(key, value)
            self.saveSettings()
        else:
            print(f'Settings.Model: Invalid value ({value}) for setting: {key}')

    def get(self, key):
        return self.model.settings_data[key]["value"]

    def checkValue(self, key, value):
        _type = self.model.settings_data[key]['type']
        if (_type == 'SBool' and type(value) == bool) or (_type == 'SString' and type(value) == str) or (
                _type == 'SPath' and type(value) == str) or (
                _type == 'SNumeric' and (type(value) == float or type(value) == int)):
            return True
        return False
