import os
import sys

import multitasking
import wget


def bar_progress(current, total, width=80):
  progress_message = "%d%% [%d / %d] МБайт" % (current / total * 100, current / 1048576, total / 1048576)
  sys.stdout.write("\r" + progress_message)
  sys.stdout.flush()


def create_dir(path):
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)


class Downloader:

    def __init__(self, url, path, filename):
        self.path = path
        self.filename = filename
        self.url = url

        self.isStarted = False
        self.isPaused = False

    @multitasking.task
    def start(self):
        if not self.isStarted:
            create_dir(self.path)
            fullpath = os.path.join(self.path, self.filename)
            self.isStarted = True
            wget.download(self.url, out=fullpath, bar=bar_progress)

    def pause(self):
        pass

    def stop(self):
        pass
