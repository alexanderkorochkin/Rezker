import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.screen import MDScreen
from libs.Common.observer import Observer


class LoaderLabel(MDLabel):
    default_size_x = NumericProperty(100)
    default_size_y = NumericProperty(20)
    loading_color = ListProperty([0.15, 0.15, 0.15, 0.5])

    def __init__(self, **kwargs):
        super(LoaderLabel, self).__init__(**kwargs)
        self.bind(text=self.on_text_change)

    def on_text_change(self, instance, value):
        if value:
            self.loading_color = [1, 1, 1, 0.0]
        else:
            self.loading_color = [0.15, 0.15, 0.15, 0.5]


class ItemScreen(MDScreen, Observer):
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

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)

    def model_is_changed(self, what='all'):
        if what == 'itemBaseInformation' or what == 'all':
            self.url = self.model.itemBaseInformation['url']
            self.hdrezka_id = self.model.itemBaseInformation['id']
            self.thumbnail = self.model.itemBaseInformation['thumbnail']
            self.title = self.model.itemBaseInformation['title']
            self.title_en = self.model.itemBaseInformation['title_en']
            self.date = self.model.itemBaseInformation['date']
            self.year = f" ({self.date.split(' ')[-2]})" if self.date else ''
            self.type = self.model.itemBaseInformation['type']
            self.sub_type = self.model.itemBaseInformation['sub_type']
            self.rate = self.model.itemBaseInformation['rate']
            self.genre = self.model.itemBaseInformation['genre']
            self.tagline = self.model.itemBaseInformation['tagline']
            self.age = self.model.itemBaseInformation['age']
            self.duration = self.model.itemBaseInformation['duration']
            self.description = self.model.itemBaseInformation['description']


Builder.load_file(os.path.join(os.path.dirname(__file__), "item.kv"))
