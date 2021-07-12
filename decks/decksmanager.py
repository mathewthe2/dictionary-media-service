
from decks.decks import Decks 
from config import DECK_CATEGORIES, DEFAULT_CATEGORY, REDIS_URL
import json
import redis
r = redis.StrictRedis.from_url(REDIS_URL, db=0)

SENTENCE_KEYS_FOR_LISTS = ['pretext', 'posttext', 'word_list', 'word_base_list', 'translation_word_list', 'translation_word_base_list']

class DecksManager:
    def __init__(self, category=DEFAULT_CATEGORY):
        self.decks = {}
        self.category = category

    def set_category(self, category):
        self.category = category

    def load_decks(self):
        for deck_category in DECK_CATEGORIES:
            self.decks[deck_category] = Decks(
                category=deck_category, 
                path=DECK_CATEGORIES[deck_category]["path"],
                has_image=DECK_CATEGORIES[deck_category]["has_image"],
                has_sound=DECK_CATEGORIES[deck_category]["has_sound"])
            self.decks[deck_category].load_decks()

    def get_deck_by_name(self, deck_name):
        return self.decks[self.category].get_deck_by_name(deck_name)

    def get_sentences(self, sentence_ids):
        sentences = []
        with r.pipeline() as pipe:
            for sentence_id in sentence_ids:
                pipe.hgetall(self.category + '-' + sentence_id)
            for b64data in pipe.execute():
                data = { key.decode(): val.decode() for key, val in b64data.items() }
                sentence = {}
                for key, val in data.items():
                    sentence[key] = json.loads(val) if key in SENTENCE_KEYS_FOR_LISTS else val
                sentences.append(sentence)
        return sentences
        
    def get_sentence(self, sentence_id):
        sentences = self.get_sentences([sentence_id])
        if len(sentences) > 0:
            return sentences[0]
        else:
            return None

    def get_sentence_map(self):
        return self.decks[self.category].get_sentence_map()

    def get_sentence_translation_map(self):
        return self.decks[self.category].get_sentence_translation_map()