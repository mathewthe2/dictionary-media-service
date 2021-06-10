from glob import glob
from pathlib import Path
import json
from config import EXAMPLE_PATH

class Tagger:
    def __init__(self):
        self.tag_map = {}
        self.deck_to_tag_map = {}

    def load_tags(self):
        deck_folders = glob(str(EXAMPLE_PATH) + '/*/')
        for deck_folder in deck_folders:
            deck_name = Path(deck_folder).name
            tags = self.load_tags_for_deck(deck_folder)
            self.deck_to_tag_map[deck_name] = tags
            for tag in tags:
                if tag not in self.tag_map:
                    self.tag_map[tag] = set()
                self.tag_map[tag].add(deck_name)

    def load_tags_for_deck(self, filename):
        file = Path(EXAMPLE_PATH, filename, 'tags.json')
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
            return data

    def get_tags_by_deck(self, deck):
        return [] if deck not in self.deck_to_tag_map else self.deck_to_tag_map[deck]

    def get_decks_by_tags(self, tags):
        results =  [self.tag_map.get(tag, set()) for tag in tags]
        return [] if not results else list(set.union(*results))