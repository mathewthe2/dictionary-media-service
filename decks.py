from glob import glob
from config import EXAMPLE_PATH, MEDIA_FILE_HOST, CONTEXT_RANGE
import json
import string
from pathlib import Path

class Decks:
    def __init__(self):
        self.sentences = {}
        self.sentence_map = {}
        self.sentence_translation_map = {}

    def get_sentence(self, sentence_id):
        if sentence_id in self.sentences:
            return self.sentences[sentence_id]
        else:
            return None

    def get_sentence_map(self):
        return self.sentence_map

    def get_sentence_translation_map(self):
        return self.sentence_translation_map

    def load_decks(self):
        deck_folders = glob(str(EXAMPLE_PATH) + '/*/')
        for deck_folder in deck_folders:
            self.load_deck_by_path(deck_folder)
    
    def load_deck_by_path(self, path):
        sentences = []
        file = Path(path, 'data.json')
        with open(file, encoding='utf-8') as f:
            sentences = json.load(f)
        
        for index, sentence in enumerate(sentences):
            sentence = self.parse_sentence(sentence)
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
            self.sentences[sentence["id"]] = sentence

    def parse_sentence(self, sentence):
        # image
        image_path = '{}/anime/{}/media/{}'.format(MEDIA_FILE_HOST, sentence['deck_name'], sentence['image'])
        sentence['image_url'] = image_path
        
        # sound
        sound_path = '{}/anime/{}/media/{}'.format(MEDIA_FILE_HOST, sentence['deck_name'], sentence['sound'])
        sentence['sound_url'] = sound_path
        return sentence
    
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
