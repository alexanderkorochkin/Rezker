import os
import sys

from kivy.resources import resource_add_path, resource_find

if hasattr(sys, '_MEIPASS'):
    resource_add_path(os.path.join(sys._MEIPASS))
if hasattr(sys, '_MEIPASS') or sys.__stdout__ is None or sys.__stderr__ is None:
    os.environ['KIVY_NO_CONSOLELOG'] = '1'
    os.environ['KIVY_LOG_MODE'] = 'PYTHON'

from libs.rezker import rezkerApp


if __name__ == '__main__':
    rezkerApp.run()
