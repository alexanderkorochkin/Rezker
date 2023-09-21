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

    def get_screen(self):
        return self.view

    @multitasking.task
    def getItemDataFromURL(self, url):
        self.model.clearData()
        item = HdRezkaApi(url)

        try:
            sub_type = url.split('/')[-3]
        except Exception:
            sub_type = ''

        if sub_type == 'animation':
            sub_type = 'Аниме'
            if str(item.type) == 'movie':
                sub_type = 'Мультфильмы (аниме)'
            else:
                sub_type = 'Мультсериалы (аниме)'
        elif sub_type == 'films':
            sub_type = 'Фильмы'
        elif sub_type == 'series':
            sub_type = 'Сериалы'
        elif sub_type == 'cartoons':
            if str(item.type) == 'movie':
                sub_type = 'Мультфильмы'
            else:
                sub_type = 'Мультсериалы'

        self.model.itemBaseInformation = {
            'url': url,
            'id': item.id,
            'thumbnail': item.thumbnail,
            'title': item.title,
            'title_en': item.title_en,
            'date': item.date,
            'type': str(item.type),
            'sub_type': sub_type,
            'rate': str(item.rating),
            'genre': item.genre,
            'tagline': item.tagline,
            'age': item.age,
            'duration': item.duration,
            'description': item.description
        }.copy()


