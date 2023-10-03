import json
import os

import multitasking
from kivy import Logger


class SettingsModel:

    def __init__(self):
        self._settings_data = {}
        self.view = None

    @property
    def settings_data(self):
        return self._settings_data

    def set(self, key, value):
        self._settings_data[key]['value'] = value
        self.view.updateSetting(key, value)
