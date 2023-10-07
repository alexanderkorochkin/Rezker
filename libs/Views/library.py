import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.screen import MDScreen
from libs.Common.observer import Observer


class LibraryItem(MDBoxLayout):
    controller = ObjectProperty()
    model = ObjectProperty()

    url = StringProperty('')
    hdrezka_id = StringProperty('')
    thumbnail = StringProperty('')
    title = StringProperty('')
    type = StringProperty('')
    sub_type = StringProperty('')
    summary_info = StringProperty('')
    quality = StringProperty('')
    isLibrary = BooleanProperty(True)


class RVLibraryItems(MDRecycleView):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, model, controller, **kwargs):
        super(RVLibraryItems, self).__init__(**kwargs)
        self.model = model
        self.controller = controller
        self.data = []


class LibraryScreen(MDScreen, Observer):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)
        self.recycleList = RVLibraryItems(self.model, self.controller)
        self.ids.library_screen_box.add_widget(self.recycleList)

    def model_is_changed(self):
        self.recycleList.data = self.model.data
        self.ids.library_empty_indicator.text = ''


Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/library.kv"))
