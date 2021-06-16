import json
import zipfile
from pathlib import Path
from config import DICTIONARY_PATH

class Dictionary:
    def __init__(self):
        self.dictionary_map = {}

    def is_entry(self, word):
        return word in self.dictionary_map

    def get_first_entry(self, word):
        return self.dictionary_map[word][0]

    def load_dictionary_by_path(self, dictionary_path):
        output_map = {}
        archive = zipfile.ZipFile(dictionary_path, 'r')

        result = list()
        for file in archive.namelist():
            if file.startswith('term'):
                with archive.open(file) as f:
                    data = f.read()
                    d = json.loads(data.decode("utf-8"))
                    result.extend(d)

        for entry in result:
            if (entry[0] in output_map):
                output_map[entry[0]].append(entry)
            else:
                output_map[entry[0]] = [entry] # Using headword as key for finding the dictionary entry
        return output_map

    def load_dictionary(self, dictionary_name):
        dictionary_path = Path(DICTIONARY_PATH, dictionary_name + '.zip')
        if dictionary_path:
            self.dictionary_map = self.load_dictionary_by_path(str(dictionary_path))
        else:
            print('failed to find path for dictionary')

    def get_definition(self, word):
        return self.parse_dictionary_entries(self.dictionary_map[word])

    def parse_dictionary_entries(self, entries):
        return  [{
            'headword': entry[0],
            'reading': entry[1],
            'tags': entry[2],
            'glossary_list': entry[5],
            'sequence': entry[6],
        } for entry in entries]