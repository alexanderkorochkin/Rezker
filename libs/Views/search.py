import math
import os

from kivy.animation import Animation
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, partial
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from libs.Common.observer import Observer
from libs.Views.common import HoverMDFlatButton
from libs.Views.library import RVLibraryItems


class FloatingButton(HoverMDFlatButton):

    anim = None

    def deAnim(self, *args):
        self.anim = None

    @mainthread
    def make_visible(self, scroll):
        if self.anim is None:
            self.disabled = False
            self.anim = (Animation(opacity=1, d=0.3))
            self.anim.bind(on_complete=self.deAnim)
            self.anim.start(self)

    @mainthread
    def make_invisible(self, scroll):
        if self.anim:
            self.anim.cancel(self)
            self.anim = None
        self.disabled = True
        self.opacity = 0


class SearchScreen(MDScreen, Observer):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.model.add_observer(self)
        self.recycleList = RVLibraryItems(self.model, self.controller)
        self.ids.search_screen_box.add_widget(self.recycleList)
        self.next_results_btn = FloatingButton(text='Загрузить еще', on_release=self.controller.NextResults)
        self.recycleList.fbind('scroll_y', self.checkScroll)
        self.recycleList.fbind('height', self.checkHeight)

    def checkHeight(self, *args):
        sv_height = self.recycleList.height
        vp_height = self.recycleList.viewport_size[1]

        if vp_height <= sv_height:
            self.next_results_btn.make_visible(self)

    def checkScroll(self, *args):
        if args[1] <= 0.05:
            self.next_results_btn.make_visible(self)
        else:
            self.next_results_btn.make_invisible(self)

    @mainthread
    def EnableNextResultsButton(self):
        self.add_widget(self.next_results_btn)
        self.checkScroll(*(None, self.recycleList.scroll_y))

    @mainthread
    def DisableNextResultsButton(self):
        self.next_results_btn.make_invisible(self)
        self.remove_widget(self.next_results_btn)

    def adjust_scroll(self, bottom, dt):
        sv_height = self.recycleList.height
        vp_height = self.recycleList.viewport_size[1]
        self.recycleList.scroll_y = bottom / (vp_height - sv_height)
        self.checkScroll(*(None, self.recycleList.scroll_y))

    @mainthread
    def model_is_changed(self, new_len):
        default_height = self.recycleList.ids.recycle_layout.default_size[1] + 10
        old_len = len(self.recycleList.data)
        cols = self.controller.app.COLS_LIBRARY
        rows_old = math.ceil(old_len / cols)
        rows_new = math.ceil(new_len / cols)
        delta_rows = rows_new - rows_old

        sv_height = self.recycleList.height
        vp_height = self.recycleList.viewport_size[1]
        bottom = self.recycleList.scroll_y * (vp_height - sv_height)

        self.recycleList.data = self.model.data.copy()

        if vp_height > sv_height and delta_rows >= 0:
            Clock.schedule_once(partial(self.adjust_scroll, bottom + default_height * delta_rows), -1)


Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/search.kv"))
