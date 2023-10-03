import json
import time
import urllib.request
from collections import defaultdict
from urllib.parse import quote

import multitasking
import phantomjs
from parsel import Selector

from httpx import Client

import requests
import validators
from bs4 import BeautifulSoup
from kivy.uix.screenmanager import NoTransition
from requests_html import HTMLSession
from selenium import webdriver

from libs.Common.utils import getItemDataFromURL
from libs.Models.menu import MenuModel
from libs.Views.menu import MenuView


class MenuController:

    def __init__(self, app):
        self.app = app
        self.model = MenuModel()
        self.view = MenuView(app=self.app, controller=self, model=self.model)
        self.loadSpinner = None

        self.last_request = ''

    def get_screen(self):
        return self.view

    @multitasking.task
    def search(self, request):
        if request == 'test':
            self.app.rootScreen.screens['library']['controller'].add_item(getItemDataFromURL(self.app.provider('https://hdrezkawer.org/films/fiction/2259-interstellar-2014.html')))
        else:
            self.view.set_cursor_to_start()
            if validators.url(request):
                self.app.rootScreen.openItem(request)
            else:
                self.app.rootScreen.openSearch(request)

    def screen_back(self):
        self.app.rootScreen.set_screen(self.model.last_screen, no_last=True)

