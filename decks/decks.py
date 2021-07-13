from glob import glob
from config import EXAMPLE_PATH, MEDIA_FILE_HOST, CONTEXT_RANGE
import json
import string
from pathlib import Path

class Decks:
    def __init__(self, category="anime", path=EXAMPLE_PATH, has_image=True, has_sound=True):
        self.sentence_map = {}
        self.sentence_translation_map = {}
        self.category = category
        self.path = path
        self.has_image = has_image
        self.has_sound = has_sound

    def get_sentence_map(self):
        return self.sentence_map

    def get_sentence_translation_map(self):
        return self.sentence_translation_map

    def get_deck_by_name(self, deck_name):
        sentences = []
        file = Path(self.path, deck_name, 'data.json')
        with open(file, encoding='utf-8') as f:
            sentences = json.load(f)
        return sentences

    def load_decks(self):
        deck_folders = glob(str(self.path) + '/*/')
        for deck_folder in deck_folders:
            self.load_deck_by_path(deck_folder)
    
    def load_deck_by_path(self, path):
        sentences = []
        file = Path(path, 'data.json')
        with open(file, encoding='utf-8') as f:
            sentences = json.load(f)
        
        for index, sentence in enumerate(sentences):
            pretext_sentences  = sentences[0:index] if index < CONTEXT_RANGE else sentences[index-CONTEXT_RANGE:index] 
            posttext_sentences = []
            if index < len(sentences):
                posttext_sentences = sentences[index+1:len(sentences)] if index+CONTEXT_RANGE > len(sentences) else sentences[index+1:index+CONTEXT_RANGE] 
            sentence["pretext"] = [sentence["id"] for sentence in pretext_sentences]
            sentence["posttext"] = [sentence["id"] for sentence in posttext_sentences]
            if 'word_base_list' in sentence:
                self.sentence_map = self.map_sentence(sentence['word_base_list'], sentence['id'], self.sentence_map)
            if 'translation_word_base_list' in sentence:
                self.sentence_translation_map = self.map_sentence(sentence['translation_word_base_list'], sentence['id'], self.sentence_translation_map)
    
    def update_deck_on_redis(self, path):
        sentences = []
        file = Path(path, 'data.json')
        with open(file, encoding='utf-8') as f:
            sentences = json.load(f)
        from config import REDIS_URL
        import redis
        r = redis.StrictRedis.from_url(REDIS_URL, db=0)
        with r.pipeline() as pipe:
            for index, sentence in enumerate(sentences):
                pretext_sentences  = sentences[0:index] if index < CONTEXT_RANGE else sentences[index-CONTEXT_RANGE:index] 
                posttext_sentences = []
                if index < len(sentences):
                    posttext_sentences = sentences[index+1:len(sentences)] if index+CONTEXT_RANGE > len(sentences) else sentences[index+1:index+CONTEXT_RANGE] 
                sentence["pretext"] = [sentence["id"] for sentence in pretext_sentences]
                sentence["posttext"] = [sentence["id"] for sentence in posttext_sentences]
                if 'word_base_list' in sentence:
                    self.sentence_map = self.map_sentence(sentence['word_base_list'], sentence['id'], self.sentence_map)
                if 'translation_word_base_list' in sentence:
                    self.sentence_translation_map = self.map_sentence(sentence['translation_word_base_list'], sentence['id'], self.sentence_translation_map)
            
                filtered_sentence = self.filter_fields(sentence, ['id'])
                for key in filtered_sentence:
                    value = filtered_sentence[key]
                    if type(value) == list:
                        value = json.dumps(value, ensure_ascii=False)
                    pipe.hset(self.category + '-' + sentence["id"], key, value)
            pipe.execute()

    def filter_fields(self, sentence, excluded_fields):
        filtered_sentence = {}
        for key in sentence:
            if key not in excluded_fields:
                filtered_sentence[key] = sentence[key]
        return filtered_sentence
    
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
