import os
import sys
import multitasking
import wget
from libs.Models.item import ItemModel
from libs.Views.item import ItemScreen
from libs.hdrezkalib.hdrezka import HdRezkaApi

multitasking.set_max_threads(multitasking.config["CPU_CORES"] * 5)


class ItemController:

    def __init__(self, app, name):
        self.app = app
        self.model = ItemModel()
        self.view = ItemScreen(controller=self, model=self.model, name=name)
        self.item = None

    def get_screen(self):
        return self.view

    def chooseTranslation(self, translation):
        self.model.activeTranslation = translation

    def addDownload(self, translation):
        self.app.rootScreen.downloadsController.addDownload(self.model.itemBaseInformation, translation)

    @multitasking.task
    def getItemDataFromURL(self, url):
        self.model.clearData()
        self.item = HdRezkaApi(url)

        try:
            sub_type = url.split('/')[-3]
        except Exception:
            sub_type = ''

        if sub_type == 'animation':
            sub_type = 'Аниме'
            if str(self.item.type) == 'movie':
                sub_type = 'Мультфильмы (аниме)'
            else:
                sub_type = 'Мультсериалы (аниме)'
        elif sub_type == 'films':
            sub_type = 'Фильмы'
        elif sub_type == 'series':
            sub_type = 'Сериалы'
        elif sub_type == 'cartoons':
            if str(self.item.type) == 'movie':
                sub_type = 'Мультфильмы'
            else:
                sub_type = 'Мультсериалы'

        self.model.itemBaseInformation = {
            'url': url,
            'hdrezka_id': self.item.id,
            'thumbnail': self.item.thumbnail,
            'title': self.item.title,
            'title_en': self.item.title_en,
            'date': self.item.date,
            'type': str(self.item.type),
            'sub_type': sub_type,
            'rate': str(self.item.rating),
            'genre': self.item.genre,
            'tagline': self.item.tagline,
            'age': self.item.age,
            'duration': self.item.duration,
            'description': self.item.description,
            'translations': self.item.translators,
        }.copy()
