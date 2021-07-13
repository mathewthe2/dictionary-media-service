
from decks.decks import Decks 
from config import DECK_CATEGORIES, DEFAULT_CATEGORY, REDIS_URL, MEDIA_FILE_HOST
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
    
    def update_deck_on_redis(self, deck):
        from pathlib import Path
        path = Path(DECK_CATEGORIES[self.category]["path"], deck)
        return self.decks[self.category].update_deck_on_redis(path)

    def get_deck_by_name(self, deck_name):
        return [self.parse_sentence(sentence) for sentence in self.decks[self.category].get_deck_by_name(deck_name)]

    def get_sentences(self, sentence_ids):
        sentences = []
        with r.pipeline() as pipe:
            for sentence_id in sentence_ids:
                pipe.hgetall(self.category + '-' + sentence_id)
            for index, b64data in enumerate(pipe.execute()):
                data = { key.decode(): val.decode() for key, val in b64data.items() }
                sentence = {}
                for key, val in data.items():
                    sentence[key] = json.loads(val) if key in SENTENCE_KEYS_FOR_LISTS else val
                sentence["id"] = sentence_ids[index]
                sentences.append(self.parse_sentence(sentence))
        return sentences
        
    def get_sentence(self, sentence_id):
        sentences = self.get_sentences([sentence_id])
        if len(sentences) > 0:
            return sentences[0]
        else:
            return None

    def parse_sentence(self, sentence):
        if sentence:
            if (self.decks[self.category].has_image):
                image_path = '{}/{}/{}/media/{}'.format(MEDIA_FILE_HOST, self.category, sentence['deck_name'], sentence['image'])
                sentence['image_url'] = image_path.replace(" ", "%20")
            
            if (self.decks[self.category].has_sound):
                sound_path = '{}/{}/{}/media/{}'.format(MEDIA_FILE_HOST, self.category, sentence['deck_name'], sentence['sound'])
                sentence['sound_url'] = sound_path.replace(" ", "%20")
        return sentence

    def get_sentence_map(self):
        return self.decks[self.category].get_sentence_map()

    def get_sentence_translation_map(self):
        return self.decks[self.category].get_sentence_translation_map()