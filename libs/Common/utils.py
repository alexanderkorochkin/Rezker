import os
import random
import subprocess
import sys

import bs4
import multitasking
import requests
from kivy.animation import Animation
from kivy.clock import mainthread
from kivy.metrics import dp
from kivy.properties import partial
from kivy.utils import platform
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.spinner import MDSpinner

from mutagen.mp4 import MP4, MP4Cover
from plyer import filechooser

from libs.hdrezkalib.hdrezka import HdRezkaApi


class Spinner:

    def __init__(self, app):
        self.app = app
        self.screen = None
        self.spinner_anim = None

        self.spinner_main = MDSpinner(
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={'center_x': .5, 'center_y': .5},
            active=True
        )
        self.label = MDFlatButton(text='', disabled=True, pos_hint={'center_x': .5, 'center_y': .5})
        self.box = MDCard(orientation='vertical', radius=[8], size_hint=(None, None), size=(dp(90), dp(90)), padding=[dp(5), dp(5), dp(5), dp(5)])
        self.content = MDAnchorLayout(md_bg_color=[0, 0, 0, 0.4], anchor_x='center', anchor_y='center')

        self.box.add_widget(self.spinner_main)
        self.box.add_widget(self.label)

        self.content.add_widget(self.box)

    @mainthread
    def start(self, screen: MDScreen, text: str = 'Загрузка'):
        self.label.text = text
        self.screen = screen
        self.content.opacity = 0
        self.screen.add_widget(self.content)
        self.spinner_anim = Animation(opacity=1, d=0.3)
        self.spinner_anim.start(self.content)

    def removeSpinner(self, *args):
        args[0].remove_widget(self.content)

    @mainthread
    def stop(self):
        self.spinner_anim = Animation(opacity=0, d=0.3)
        self.spinner_anim.bind(on_complete=partial(self.removeSpinner, self.screen))
        self.spinner_anim.start(self.content)


@multitasking.task
def open_in_explorer(path: str, mode, last_path=None):
    if os.path.exists(path):
        if 'open' in mode:
            subprocess.Popen(rf'explorer /open,"{path}"')
        elif 'select' in mode:
            subprocess.Popen(rf'explorer /select,"{path}"')
    else:
        if os.path.exists(path + '.000'):
            path = path + '.000'
            subprocess.Popen(rf'explorer /select,"{path}"')
        else:
            new_path = '\\'.join(path.split('\\')[:-1:])
            if last_path == new_path:
                print(f'Downloads.Controller: Path ({last_path}) not exists!')
                return
            open_in_explorer(new_path, 'open', path)


def remove_not_valid_chars(value, chars):
    for c in chars:
        value = value.replace(c, '.')
    return value


def getSearchItemFromSoupTag(tag: bs4.element.Tag):
    url = tag["data-url"]

    parser = HdRezkaApi(tag)
    try:
        sub_type = url.split('/')[-3]
    except Exception:
        sub_type = ''

    if sub_type == 'animation':
        if str(parser.type) == 'movie':
            sub_type = 'Мультфильмы (аниме)'
        else:
            sub_type = 'Мультсериалы (аниме)'
    elif sub_type == 'films':
        sub_type = 'Фильмы'
    elif sub_type == 'series':
        sub_type = 'Сериалы'
    elif sub_type == 'cartoons':
        if str(parser.type) == 'movie':
            sub_type = 'Мультфильмы'
        else:
            sub_type = 'Мультсериалы'

    return {
        'url': url,
        'hdrezka_id': parser.id,
        'thumbnail': parser.thumbnail,
        'title': parser.title,
        'sub_type': sub_type,
        'type': str(parser.type),
        'summary_info': parser.summary_info,
    }


def getItemDataFromURL(url):
    item = HdRezkaApi(url)
    try:
        sub_type = url.split('/')[-3]
    except Exception:
        sub_type = ''

    if sub_type == 'animation':
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

    return {
        'url': url,
        'hdrezka_id': item.id,
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
        'description': item.description,
        'translations': item.translators,
        'country': item.country,
    }


@multitasking.task
def addTags(app, info: dict):
    print(f"*MUTAGEN: Starting composing tags to file: {info['fullpath']}")

    video = MP4(info['fullpath'])

    video["\xa9day"] = info['year']
    video["\xa9cmt"] = info['translation'] + ', ' + info['quality']
    video["\xa9gen"] = info['genre']
    video["purl"] = info['url']
    video["\xa9grp"] = list(info['sub_type'].split(', '))
    if info['type'] != 'movie':
        video["\xa9nam"] = info['title'] + f" ({info['year']})" + f" [S{int(info['season'])}E{int(info['episode'])}]"
        video["tvsn"] = [int(info['season'])]
        video["tves"] = [int(info['episode'])]
    else:
        video["\xa9nam"] = info['title'] + f" ({info['year']})"

    data = requests.get(info['thumbnail']).content
    extension = info["thumbnail"].split(".")[-1]
    if extension == 'jpg':
        cover_format = MP4Cover.FORMAT_JPEG
    elif extension == 'png':
        cover_format = MP4Cover.FORMAT_PNG
    else:
        cover_format = MP4Cover.FORMAT_JPEG
    temp_image_path = app.database.user_file(f'cover_temp_{random.randint(0, 999999)}.{extension}')
    f = open(temp_image_path, 'wb')
    f.write(data)
    f.close()

    with open(temp_image_path, "rb") as f:
        video["covr"] = [
            MP4Cover(f.read(), imageformat=cover_format)
        ]

    video.save()
    f.close()
    os.remove(temp_image_path)
    print(f"*MUTAGEN: Composing is finished!")


def dialogEnterFile(callback=None):
    filechooser.open_file(on_selection=callback)


def dialogEnterDir(callback=None):
    if platform == 'win':
        try:
            import win32gui
            from win32comext.shell import shellcon, shell

            BIF_EDITBOX = shellcon.BIF_EDITBOX
            BIF_NEWDIALOGSTYLE = 0x00000040
            pidl, display_name, image_list = shell.SHBrowseForFolder(
                win32gui.GetDesktopWindow(),
                None,
                "Выберите папку...",
                BIF_NEWDIALOGSTYLE | BIF_EDITBOX, None, None
            )
            out = str(shell.SHGetPathFromIDList(pidl).decode('Windows-1251'))
            callback([out])
        except Exception:
            pass
    else:
        filechooser.choose_dir(on_selection=callback)


def create_dir(path):
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)


def str_to_class(module, class_name: str):
    if module is None:
        module = __name__
    return getattr(sys.modules[module], class_name)


keycodes = {
        # specials keys
        'backspace': 8, 'tab': 9, 'enter': 13, 'rshift': 303, 'shift': 304,
        'alt': 308, 'rctrl': 306, 'lctrl': 305,
        'super': 309, 'alt-gr': 307, 'compose': 311, 'pipe': 310,
        'capslock': 301, 'escape': 27, 'spacebar': 32, 'pageup': 280,
        'pagedown': 281, 'end': 279, 'home': 278, 'left': 276, 'up':
        273, 'right': 275, 'down': 274, 'insert': 277, 'delete': 127,
        'numlock': 300, 'print': 144, 'screenlock': 145, 'pause': 19,

        # a-z keys
        'a': 97, 'b': 98, 'c': 99, 'd': 100, 'e': 101, 'f': 102, 'g': 103,
        'h': 104, 'i': 105, 'j': 106, 'k': 107, 'l': 108, 'm': 109, 'n': 110,
        'o': 111, 'p': 112, 'q': 113, 'r': 114, 's': 115, 't': 116, 'u': 117,
        'v': 118, 'w': 119, 'x': 120, 'y': 121, 'z': 122,

        # 0-9 keys
        '0': 48, '1': 49, '2': 50, '3': 51, '4': 52,
        '5': 53, '6': 54, '7': 55, '8': 56, '9': 57,

        # numpad
        'numpad0': 256, 'numpad1': 257, 'numpad2': 258, 'numpad3': 259,
        'numpad4': 260, 'numpad5': 261, 'numpad6': 262, 'numpad7': 263,
        'numpad8': 264, 'numpad9': 265, 'numpaddecimal': 266,
        'numpaddivide': 267, 'numpadmul': 268, 'numpadsubstract': 269,
        'numpadadd': 270, 'numpadenter': 271,

        # F1-15
        'f1': 282, 'f2': 283, 'f3': 284, 'f4': 285, 'f5': 286, 'f6': 287,
        'f7': 288, 'f8': 289, 'f9': 290, 'f10': 291, 'f11': 292, 'f12': 293,
        'f13': 294, 'f14': 295, 'f15': 296,

        # other keys
        '(': 40, ')': 41,
        '[': 91, ']': 93,
        '{': 123, '}': 125,
        ':': 58, ';': 59,
        '=': 61, '+': 43,
        '-': 45, '_': 95,
        '/': 47, '*': 42,
        '?': 47,
        '`': 96, '~': 126,
        '´': 180, '¦': 166,
        '\\': 92, '|': 124,
        '"': 34, "'": 39,
        ',': 44, '.': 46,
        '<': 60, '>': 62,
        '@': 64, '!': 33,
        '#': 35, '$': 36,
        '%': 37, '^': 94,
        '&': 38, '¬': 172,
        '¨': 168, '…': 8230,
        'ù': 249, 'à': 224,
        'é': 233, 'è': 232,
    }