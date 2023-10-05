import os, sys
from kivy.resources import resource_add_path, resource_find

from libs.rezker import rezkerApp


if __name__ == '__main__':
    try:
        if hasattr(sys, '_MEIPASS'):
            resource_add_path(os.path.join(sys._MEIPASS))
        rezkerApp.run()
    except Exception as e:
        print(e)
        input("Press enter...")

# TODO Открыть папку, скопировать ссылку в загрузках, добавить размер файла и размер скачанного
# TODO Библиотека
# TODO Поисковая строка
# TODO Последние запросы в поисковой строке
# TODO Реализовать базу данных для библиотеки

