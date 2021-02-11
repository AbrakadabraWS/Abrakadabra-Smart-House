import json

class JSON_gen(object):

    def __init__(self, file = 'config.json'):
        """ Constructor """
        self._file = file
        try:
            f = open(self._file)
            f.close()
        except OSError:
            with open(self._file, 'w'):
                print('JSON file created')

    def write_to_JSON(self, config):# создает фаил и сразу прописыает весь словарь
        with open(self._file, 'w') as f:
            json.dump(config, f)
            print('written to the JSON')

    def read_config(self): # читает фаил конфигурации и возвращает словарь
        with open(self._file, 'r') as f:
            config = json.load(f)
        return config

    def change_config(self, key, value): # читает фаил и изменяет заданную переменную словаря, если такой нет то создает новую
        with open(self._file, 'r') as f:
            config = json.load(f)
        #edit the data
        if config.get(key) != None:
            config[key] = value
            print('The "' + key + '" value in the JSON has been changed')
        else:
            config.setdefault(key, value)
            print('Create "' + key + '" with the value "' + value + '"')
        #write it back to the file
        with open(self._file, 'w') as f:
            json.dump(config, f)
            print('writing to the JSON is complete')
