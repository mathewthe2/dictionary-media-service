
from decks.decks import Decks 
from config import DECK_CATEGORIES, DEFAULT_CATEGORY, SENTENCE_FIELDS, MEDIA_FILE_HOST, SENTENCE_KEYS_FOR_LISTS, SENTENCES_LIMIT
import json
import sqlite3

class DecksManager:
    def __init__(self, category=DEFAULT_CATEGORY):
        self.decks = {}
        self.category = category
        self.con = sqlite3.connect(":memory:")
        self.cur = self.con.cursor()
        self.cur.execute("create table sentences ({})".format(','.join(SENTENCE_FIELDS)))

    def set_category(self, category):
        self.category = category

    def load_decks(self):
        for deck_category in DECK_CATEGORIES:
            self.decks[deck_category] = Decks(
                category=deck_category, 
                path=DECK_CATEGORIES[deck_category]["path"],
                has_image=DECK_CATEGORIES[deck_category]["has_image"],
                has_sound=DECK_CATEGORIES[deck_category]["has_sound"])
            self.decks[deck_category].load_decks(self.cur)

    def get_deck_by_name(self, deck_name):
        return [self.parse_sentence(sentence) for sentence in self.decks[self.category].get_deck_by_name(deck_name)]

    def get_sentences(self, sentence_ids):
        sentences = []
        search_list = [self.category + '-' + sentence_id for sentence_id in sentence_ids]
        search_list = search_list[:SENTENCES_LIMIT]
        self.cur.execute("select * from sentences where id in ({seq})".format(
            seq=','.join(['?']*len(search_list))), search_list)
        result = self.cur.fetchall()
        for sentence_index, sentence_tuple in enumerate(result):
            sentence = {}
            for data_index, value in enumerate(sentence_tuple):
                key = SENTENCE_FIELDS[data_index]
                sentence[SENTENCE_FIELDS[data_index]] = value
                if value == '':
                    sentence[key] = ''
                else:
                    sentence[key] = json.loads(value) if key in SENTENCE_KEYS_FOR_LISTS else value
            sentence["id"] = sentence_ids[sentence_index]
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