from glob import glob
from config import EXAMPLE_PATH, MEDIA_FILE_HOST
import json
import string
from pathlib import Path

class Decks:
    def __init__(self):
        self.deck_map = {}
        self.sentence_map = {}
        self.sentence_translation_map = {}

    def get_deck_map(self):
        return self.deck_map

    def get_sentence_map(self):
        return self.sentence_map

    def get_sentence_translation_map(self):
        return self.sentence_translation_map

    def load_decks(self):
        deck_folders = glob(str(EXAMPLE_PATH) + '/*/')
        for deck_folder in deck_folders:
            self.load_deck_by_path(deck_folder)
    
    def load_deck_by_path(self, path):
        decks = []
        file = Path(path, 'data.json')
        with open(file, encoding='utf-8') as f:
            decks = json.load(f)
        
        for deck in decks:
            deck = self.parse_deck(deck)
            if 'word_base_list' in deck:
                self.sentence_map = self.map_sentence(deck['word_base_list'], deck['id'], self.sentence_map)
            if 'translation_word_base_list' in deck:
                self.sentence_translation_map = self.map_sentence(deck['translation_word_base_list'], deck['id'], self.sentence_translation_map)
            self.deck_map[deck["id"]] = deck

    def parse_deck(self, deck):
        # image
        image_path = '{}/anime/{}/media/{}'.format(MEDIA_FILE_HOST, deck['deck_name'], deck['image'])
        deck['image_url'] = image_path
        
        # sound
        sound_path = '{}/anime/{}/media/{}'.format(MEDIA_FILE_HOST, deck['deck_name'], deck['sound'])
        deck['sound_url'] = sound_path
        return deck
    
    def map_sentence(self, words, example_id, output_map):
        for (index, word) in enumerate(words):
            is_repeat = words.index(word) != index
            if is_repeat:
                continue
            if word in string.punctuation or word in '！？。、（）':
                continue
            if word not in output_map:
                output_map[word] = set()
            output_map[word].add(example_id)
        return output_map
