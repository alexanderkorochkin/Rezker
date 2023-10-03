import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.screen import MDScreen
from libs.Common.observer import Observer


class DownloadsItem(MDBoxLayout):
    controller = ObjectProperty()
    model = ObjectProperty()

    url = StringProperty('')
    hdrezka_id = StringProperty('')
    thumbnail = StringProperty('')
    title = StringProperty('')
    title_en = StringProperty('')
    date = StringProperty('')
    year = StringProperty('')
    type = StringProperty('')
    sub_type = StringProperty('')
    rate = StringProperty('')
    genre = StringProperty('')
    tagline = StringProperty('')
    age = StringProperty('')
    duration = StringProperty('')
    description = StringProperty('')

    downloader = ObjectProperty(None)
    download_id = StringProperty('')
    link = StringProperty('')
    fullpath = StringProperty('')
    status = StringProperty('None')
    progress = NumericProperty(0)
    speed = StringProperty('0')
    remaining_time = StringProperty('∞')
    total_size = StringProperty('0')
    downloaded_size = StringProperty('0')
    doRemove = BooleanProperty(False)

    season = StringProperty('')
    episode = StringProperty('')


class RVDownloadsItems(MDRecycleView):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, model, controller, **kwargs):
        super(RVDownloadsItems, self).__init__(**kwargs)
        self.model = model
        self.controller = controller
        self.data = []


class DownloadsScreen(MDScreen, Observer):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)
        self.recycleList = RVDownloadsItems(self.model, self.controller)
        self.ids.downloads_screen_box.add_widget(self.recycleList)

    def model_is_changed(self):
        if len(self.recycleList.data) == len(self.model.data):
            self.recycleList.data = self.model.data.copy()
            self.recycleList.refresh_from_data()
        else:
            self.recycleList.data = []
            self.recycleList.data = self.model.data.copy()
        self.ids.downloads_empty_indicator.text = ''


Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/downloads.kv"))
