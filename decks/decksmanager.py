
from decks.decks import Decks 
from config import DECK_CATEGORIES

class DecksManager:
    def __init__(self):
        self.decks = {}
        self.category = 'anime'

    def set_category(self, category):
        self.category = category

    def load_decks(self):
        # TODO: refactor to combine anime and literature deck into one class
        for deck_category in DECK_CATEGORIES:
            self.decks[deck_category] = Decks(
                category=deck_category, 
                path=DECK_CATEGORIES[deck_category]["path"],
                has_image=DECK_CATEGORIES[deck_category]["has_image"],
                has_sound=DECK_CATEGORIES[deck_category]["has_sound"])
            self.decks[deck_category].load_decks()
        
        # anime_decks = AnimeDecks()
        # anime_decks.load_decks()
        # self.decks['anime'] = anime_decks
        # literature_decks = LiteratureDecks()
        # literature_decks.load_decks()
        # self.decks['literature'] = literature_decks

    def get_sentence(self, sentence_id):
        return self.decks[self.category].get_sentence(sentence_id)

    def get_sentence_map(self):
        return self.decks[self.category].get_sentence_map()

    def get_sentence_translation_map(self):
        return self.decks[self.category].get_sentence_translation_map()