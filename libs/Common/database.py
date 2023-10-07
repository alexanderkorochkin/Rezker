import os

from plyer import storagepath

from libs.Common.utils import create_dir


class DataManager:
    _user_folder = os.path.join(os.path.normpath(storagepath.get_home_dir()), 'HDRezker')

    def __init__(self):
        create_dir(self._user_folder)

    @property
    def settings_file(self):
        return self.user_file('settings.json')

    @property
    def library_file(self):
        return self.user_file('library.json')

    def user_folder(self):
        return self._user_folder

    def thumbnail_cache(self, image: str):
        return self.user_file(*('thumbnail_cache', image))

    def user_file(self, *paths):
        if '.' in paths[-1]:
            create_dir(os.path.join(self._user_folder, *paths[:-1]))
            path = os.path.join(self._user_folder, *paths)
            return path
        else:
            print(f'DataManager: Path: {os.path.join(self._user_folder, *paths)} is not a link to file!')
