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
        self.view.set_cursor_to_start()
        if request:
            if validators.url(request):
                self.app.rootScreen.openItem(request)
            else:
                self.app.rootScreen.openSearch(request)

    def screen_next(self):
        next_screen, request = self.model.to_next_screen()
        if request:
            self.view.set_input_text(str(request))
        else:
            self.view.set_input_text('')
        self.app.rootScreen.set_screen(next_screen, request, simple=True)

    def screen_back(self):
        back_screen, request = self.model.to_back_screen()
        if request:
            self.view.set_input_text(str(request))
        else:
            self.view.set_input_text('')
        self.app.rootScreen.set_screen(back_screen, request, simple=True)
