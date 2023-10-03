import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from libs.Common.observer import Observer
from libs.Views.library import RVLibraryItems


class SearchScreen(MDScreen, Observer):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)
        self.recycleList = RVLibraryItems(self.model, self.controller)
        self.ids.search_screen_box.add_widget(self.recycleList)

    def model_is_changed(self):
        self.recycleList.data = self.model.data
        if len(self.recycleList.data) == 0:
            self.ids.search_empty_indicator.text = 'Поиск...'
        else:
            self.ids.search_empty_indicator.text = ''


Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/search.kv"))
