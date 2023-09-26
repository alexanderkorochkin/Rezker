import os
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.chip import MDChip
from kivymd.uix.label import MDLabel
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.screen import MDScreen
from libs.Common.observer import Observer
from libs.Views.common import HoverMDFlatButton, HoverMDCard


class TranslationItem(HoverMDFlatButton):
    controller = ObjectProperty()
    model = ObjectProperty()
    translation_id = NumericProperty(0)


class RVTranslationsList(MDRecycleView):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, model, controller, **kwargs):
        super(RVTranslationsList, self).__init__(**kwargs)
        self.model = model
        self.controller = controller
        self.data = []


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
    activeTranslation = StringProperty('')

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)
        self.translationsList = RVTranslationsList(self.model, self.controller)

    def model_is_changed(self, what='all'):
        if what == 'itemBaseInformation' or what == 'all':
            self.url = self.model.itemBaseInformation['url']
            self.hdrezka_id = self.model.itemBaseInformation['hdrezka_id']
            self.thumbnail = self.model.itemBaseInformation['thumbnail']
            self.title = self.model.itemBaseInformation['title']
            self.title_en = self.model.itemBaseInformation['title_en']
            self.date = self.model.itemBaseInformation['date']
            self.year = f" ({self.model.itemBaseInformation['year']})" if self.date else ''
            self.type = self.model.itemBaseInformation['type']
            self.sub_type = self.model.itemBaseInformation['sub_type']
            self.rate = self.model.itemBaseInformation['rate']
            self.genre = self.model.itemBaseInformation['genre']
            self.tagline = self.model.itemBaseInformation['tagline']
            self.age = self.model.itemBaseInformation['age']
            self.duration = self.model.itemBaseInformation['duration']
            self.description = self.model.itemBaseInformation['description']
            if len(list(self.model.itemBaseInformation['translations'].keys())) > 0:
                if self.translationsList not in self.ids.translations_box.children:
                    self.ids.translations_box.add_widget(self.translationsList)
                self.translationsList.data.clear()
                temp = []
                for translation in list(self.model.itemBaseInformation['translations'].keys()):
                    temp.append({
                        'controller': self.controller,
                        'model': self.model,
                        'text': str(translation),
                        'new_bg_color': [1, 1, 1, 0.02],
                        'translation_id': self.model.itemBaseInformation['translations'][translation]
                    })
                    self.translationsList.data = temp.copy()
                    self.model.activeTranslation = list(self.model.itemBaseInformation['translations'].keys())[0]
            else:
                self.ids.translations_box.remove_widget(self.translationsList)
        if what == 'activeTranslation' or what == 'all':
            self.activeTranslation = str(self.model.activeTranslation)
            self.translationsList.data.clear()
            temp = []
            for translation in list(self.model.itemBaseInformation['translations'].keys()):
                temp.append({
                    'controller': self.controller,
                    'model': self.model,
                    'text': str(translation),
                    'new_bg_color': [1, 1, 1, 0.4] if translation == self.model.activeTranslation else [1, 1, 1, 0.02],
                    'translation_id': self.model.itemBaseInformation['translations'][translation]
                })
                self.translationsList.data = temp.copy()


Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/item.kv"))
