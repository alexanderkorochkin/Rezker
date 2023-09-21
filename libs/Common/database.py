import multitasking


class Database:

    path = ''

    def __init__(self, path):
        self.path = path

    # Reads data from the database
    @multitasking.task
    def readData(self):
        pass

    # Write data to the database
    @multitasking.task
    def writeData(self):
        pass

    # Returns first item with key = value
    def find_item(self, key, value):
        pass

