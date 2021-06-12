

from glob import glob
from config import EXAMPLE_PATH
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
            deck = self.parse_decks(deck)
            if 'word_base_list' in deck:
                self.sentence_map = self.map_sentence(deck['word_base_list'], deck['id'], self.sentence_map)
            if 'translation_word_base_list' in deck:
                self.sentence_translation_map = self.map_sentence(deck['translation_word_base_list'], deck['id'], self.sentence_translation_map)
            self.deck_map[deck["id"]] = deck

    def parse_decks(self, decks, text_is_japanese, word_bases, tagger):
        for deck in decks:
            deck['tags'] = tagger.get_tags_by_deck(deck['deck_name'])
            deck['word_index'] = []
            deck['translation_word_index'] = []
            if text_is_japanese:
                deck['word_index'] = [deck['word_base_list'].index(word) for word in word_bases]
            else:
                deck['translation_word_index'] = [deck['translation_word_base_list'].index(word) for word in word_bases]
        return decks

    
    def map_sentence(words, example_id, output_map):
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
