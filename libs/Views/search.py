import math
import os

from kivy.animation import Animation
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, partial, StringProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.recycleview import MDRecycleView
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


class SearchItem(MDBoxLayout):
    controller = ObjectProperty()
    model = ObjectProperty()

    url = StringProperty('')
    hdrezka_id = StringProperty('')
    thumbnail = StringProperty('')
    title = StringProperty('')
    type = StringProperty('')
    sub_type = StringProperty('')
    summary_info = StringProperty('')
    isLibrary = BooleanProperty(False)
    isDownloading = BooleanProperty(False)


class RVSearchItems(MDRecycleView):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, model, controller, **kwargs):
        super(RVSearchItems, self).__init__(**kwargs)
        self.model = model
        self.controller = controller
        self.data = []


class SearchScreen(MDScreen, Observer):
    controller = ObjectProperty()
    model = ObjectProperty()

    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.model.add_observer(self)
        self.recycleList = RVSearchItems(self.model, self.controller)
        self.ids.search_screen_box.add_widget(self.recycleList)
        self.next_results_btn = FloatingButton(text='Загрузить еще', on_release=self.controller.NextResults)
        self.recycleList.fbind('scroll_y', self.checkScroll)
        self.recycleList.fbind('height', self.checkScroll)
        Window.bind(on_size=self.checkSize)

        self.default_height = 0

    def checkSize(self, *args):
        self.model_is_changed(0)

    def checkScroll(self, *args):

        sv_height = self.recycleList.height
        vp_height = self.recycleList.children[0].size[1]

        scroll_y = args[1]

        if vp_height > sv_height:
            if scroll_y <= 0.05:
                self.next_results_btn.make_visible(self)
            else:
                self.next_results_btn.make_invisible(self)
        else:
            self.next_results_btn.make_visible(self)

    @mainthread
    def EnableNextResultsButton(self):
        self.add_widget(self.next_results_btn)

    @mainthread
    def DisableNextResultsButton(self):
        self.remove_widget(self.next_results_btn)

    def adjust_scroll(self, bottom, dt):
        sv_height = self.recycleList.height
        vp_height = self.recycleList.children[0].size[1]
        self.recycleList.scroll_y = bottom / (vp_height - sv_height)

    @mainthread
    def model_is_changed(self, new_len):
        self.default_height = self.recycleList.ids.recycle_layout.default_size[1] + 10
        old_len = len(self.recycleList.data)
        cols = self.controller.app.COLS_LIBRARY
        rows_old = math.ceil(old_len / cols)
        rows_new = math.ceil(new_len / cols)
        delta_rows = rows_new - rows_old

        if rows_old == 1:
            vp_height = self.default_height * math.ceil(len(self.recycleList.data) / self.app.COLS_LIBRARY)
        else:
            vp_height = self.recycleList.children[0].size[1]
        sv_height = self.recycleList.height
        bottom = self.recycleList.scroll_y * (vp_height - sv_height)

        if new_len != 0:
            self.recycleList.data = []
            self.recycleList.data = self.model.data.copy()

        if vp_height + self.default_height * delta_rows > sv_height and delta_rows >= 0:
            Clock.schedule_once(partial(self.adjust_scroll, bottom + self.default_height * delta_rows), -1)


Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/search.kv"))
