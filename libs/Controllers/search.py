import uuid

import multitasking
import requests
from bs4 import BeautifulSoup
from kivy.clock import Clock
from kivy.properties import partial

from libs.Common.utils import getSearchItemFromSoupTag
from libs.Models.search import SearchModel
from libs.Views.search import SearchScreen


class SearchController:

    def __init__(self, app, name):
        self.app = app
        self.model = SearchModel(self.app)
        self.view = SearchScreen(self.app, controller=self, model=self.model, name=name)

        self.active_task_id = None
        self.search_active = False

        self.last_request = ''

        self.max_number_search_results = 50
        self.soup = None
        self.request = None
        self.pages = 0
        self.page = 1
        self.last_page = -1
        self.last_count = -1

    def get_screen(self):
        return self.view

    def itemAddedToLibrary(self, url: str):
        self.model.itemAddedToLibrary(url)

    def itemRemovedFromLibrary(self, url: str):
        self.model.itemRemovedFromLibrary(url)

    def itemAddedToDownloads(self, url: str):
        self.model.itemAddedToDownloads(url)

    def itemRemovedFromDownloads(self, url: str):
        self.model.itemRemovedFromDownloads(url)

    def Search(self, request: str):
        self.last_request = request
        self.app.spinner.start(self.app.rootScreen)
        self.active_task_id = uuid.uuid4().hex
        self.model.clear_items()
        self.view.DisableNextResultsButton()
        self.request = request
        self.pages = None
        self.page = 1
        self.last_page = -1
        self.last_count = -1
        args = (self.active_task_id, True)
        if self.search_active:
            Clock.schedule_once(partial(self.search_low, *args), 1)
        else:
            self.search_low(*args)

    def NextResults(self, *args):
        self.app.spinner.start(self.app.rootScreen)
        self.view.DisableNextResultsButton()
        self.search_low(self.active_task_id, False)

    @multitasking.task
    def search_low(self, task_id, new_search: bool, *args):
        self.search_active = True

        try:
            itemsBaseInformation = []

            if self.last_page != self.page:

                if task_id != self.active_task_id:
                    self.search_active = False
                    return

                HEADERS = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47'}
                url = self.app.provider()
                r = requests.get(url, headers=HEADERS)
                cookies = r.cookies

                if task_id != self.active_task_id:
                    self.search_active = False
                    return

                url = f'{self.app.provider()}/search/?do=search&subaction=search&q={self.request}&page={self.page}'
                r = requests.get(url, cookies=cookies, headers=HEADERS)

                if task_id != self.active_task_id:
                    self.search_active = False
                    return

                self.soup = BeautifulSoup(r.text, 'html.parser')

            if self.pages is None:
                pagesTag = self.soup.find('div', {"class": "b-navigation"})
                if pagesTag:
                    self.pages = len(pagesTag.findAll("a", href=True))
                else:
                    self.pages = 1

            rootTag = self.soup.find('div', {"class": "b-content__inline_items"})
            items = rootTag.findAll("div", {"class": "b-content__inline_item"})
            items_in_page = len(items)
            self.last_page = self.page
            counter = 0
            for item in items:
                if self.last_count < counter:
                    if counter <= self.last_count + self.max_number_search_results:
                        if counter == items_in_page - 1:
                            self.page = min(self.page + 1, self.pages)
                            if self.page != self.pages:
                                self.view.EnableNextResultsButton()
                            self.last_count = -1

                        if task_id != self.active_task_id:
                            self.search_active = False
                            return

                        itemBaseInformation = getSearchItemFromSoupTag(item)

                        if task_id != self.active_task_id:
                            self.search_active = False
                            return
                        itemsBaseInformation.append(itemBaseInformation)
                    else:
                        self.last_count = counter - 1
                        self.view.EnableNextResultsButton()
                        break
                counter += 1
            if len(itemsBaseInformation) > 0:
                self.add_items(itemsBaseInformation)
        except Exception as e:
            print(f'SEARCH ERROR: {e}')
        finally:
            self.search_active = False
            self.app.spinner.stop()

    def add_items(self, itemsBaseInformation: list):
        self.model.add_items(itemsBaseInformation, self, self.model)

    def openItem(self, url):
        self.app.rootScreen.openItem(url)
