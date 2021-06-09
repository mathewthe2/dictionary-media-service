from glob import glob
from pathlib import Path
import json
from config import EXAMPLE_PATH

class Tagger:
    def __init__(self):
        self.tag_map = {}

    def load_tags(self):
        deck_folders = glob(str(EXAMPLE_PATH) + '/*/')
        for deck_folder in deck_folders:
            deck_name = Path(deck_folder).name
            tags = self.get_deck_tags(deck_folder)
            for tag in tags:
                if tag not in self.tag_map:
                    self.tag_map[tag] = set()
                self.tag_map[tag].add(deck_name)

    def get_deck_tags(self, filename):
        file = Path(EXAMPLE_PATH, filename, 'tags.json')
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
            return data

    def get_decks_by_tags(self, tags):
        results =  [self.tag_map.get(tag, set()) for tag in tags]
        return [] if not results else list(set.union(*results))