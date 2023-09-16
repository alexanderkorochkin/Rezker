import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.recycleview import RecycleView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.screen import MDScreen
from libs.Common.observer import Observer

from kivymd_extensions.akivymd.uix.loaders import AKImageLoader


class LibraryItem(MDBoxLayout):
    title = StringProperty('Title')
    year = StringProperty('year')
    genre = StringProperty('genre')
    cover = StringProperty('')
    type = StringProperty('type')
    url = StringProperty('URL')


class RecycleListItems(MDRecycleView):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, model, controller, **kwargs):
        super(RecycleListItems, self).__init__(**kwargs)
        self.model = model
        self.controller = controller
        self.data = []


class LibraryScreen(MDScreen, Observer):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)
        self.recycleList = RecycleListItems(self.model, self.controller)
        self.ids.library_screen_box.add_widget(self.recycleList)

    def model_is_changed(self):
        self.recycleList.data = self.model.data
        self.ids.library_empty_indicator.text = ''


Builder.load_file(os.path.join(os.path.dirname(__file__), "library.kv"))
