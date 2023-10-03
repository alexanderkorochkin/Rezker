import uuid

import multitasking
import requests
from bs4 import BeautifulSoup
from kivy.clock import Clock
from kivy.properties import partial

from libs.Common.utils import getItemDataFromURL
from libs.Models.search import SearchModel
from libs.Views.search import SearchScreen


class SearchController:

    def __init__(self, app, name):
        self.app = app
        self.model = SearchModel()
        self.view = SearchScreen(controller=self, model=self.model, name=name)

        self.active_task_id = None
        self.search_active = False

    def get_screen(self):
        return self.view

    def Search(self, request: str):
        self.model.clear_items()
        self.active_task_id = uuid.uuid4().hex
        args = (request, self.active_task_id)
        if self.search_active:
            Clock.schedule_once(partial(self.search_low, *args), 1)
        else:
            self.search_low(request, self.active_task_id)

    @multitasking.task
    def search_low(self, request: str, task_id, *args):
        self.search_active = True
        if task_id != self.active_task_id:
            self.search_active = False
            return
        HEADERS = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47'}
        page = 1
        url = self.app.provider()
        r = requests.get(url, headers=HEADERS)
        cookies = r.cookies

        if task_id != self.active_task_id:
            self.search_active = False
            return

        url = f'{self.app.provider()}/search/?do=search&subaction=search&q={request}&page={page}'
        r = requests.get(url, cookies=cookies, headers=HEADERS)

        if task_id != self.active_task_id:
            self.search_active = False
            return

        self.model.clear_items()
        soup = BeautifulSoup(r.text, 'html.parser')
        rootTag = soup.find('div', {"class": "b-content__inline_items"})
        for item in rootTag.findAll("div", {"class": "b-content__inline_item"}):
            if task_id != self.active_task_id:
                self.search_active = False
                return
            print(f'FOUND ITEM: {item["data-url"]}')
            temp_dict = getItemDataFromURL(self.app.provider(item["data-url"]))
            if task_id != self.active_task_id:
                self.search_active = False
                return
            self.add_item(temp_dict)
        self.search_active = False

    def add_item(self, itemBaseInformation: dict):
        self.model.add_item(itemBaseInformation, self, self.model)

    def open_item(self, url):
        self.app.rootScreen.openItem(url)
