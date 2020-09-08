command_list = []


class Command:
    def __init__(self):
        self.__keys = []
        self.description = ''
        command_list.append(self)

    @property
    def keys(self):
        return self.__keys

    @keys.setter
    def keys(self, keys_mas: list):
        for key in keys_mas:
            self.__keys.append(key.lower())

    def process(self, user_id, message):
        pass
