import json
import os
from pathlib import Path
from englishtokenizer import analyze
from glob import glob
from sudachipy import tokenizer
from sudachipy import dictionary
from config import EXAMPLE_PATH
from tagger import Tagger

tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.A

def getDeckStructure(filename):
    file = Path(EXAMPLE_PATH, filename, 'deck-structure.json')
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
        return data

def parseDeck(filename):
    deck_structure = getDeckStructure(filename)
    file = Path(EXAMPLE_PATH, category, deck, 'deck.json')
    examples = []
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
        notes = data['notes']
        deck_name = data['name']
        for note in notes:

            # segmentation
            text = note['fields'][deck_structure['text-column']]
            word_base_list = [m.normalized_form() for m in tokenizer_obj.tokenize(text, mode)]
            word_list = [m.surface() for m in tokenizer_obj.tokenize(text, mode)]
            translation = note['fields'][deck_structure['translation-column']]
            translation_tokens = analyze(translation)
            translation_word_list = translation_tokens['tokens']
            translation_word_base_list = translation_tokens['base_tokens']
            print('parsing note', note['fields'][deck_structure['id-column']])
            example = {
                'id': note['fields'][deck_structure['id-column']],
                'deck_name': deck_name,
                'sentence': text,
                'sentence_with_furigana': note['fields'][deck_structure['text-with-furigana-column']],
                'word_base_list': word_base_list,
                'word_list': word_list,
                'translation_word_list': translation_word_list,
                'translation_word_base_list': translation_word_base_list,
                'translation': translation,
                'image': note['fields'][deck_structure['image-column']].split('src="')[1].split('">')[0],
                'sound': note['fields'][deck_structure['sound-column']].split('sound:')[1].split(']')[0]
            }
            examples.append(example)

    with open(Path(EXAMPLE_PATH, filename, 'data.json'), 'w+', encoding='utf8') as outfile:
        json.dump(examples, outfile, indent=4, ensure_ascii=False)

# tagMap = {}

# def loadTags():
#     global tagMap
#     deck_folders = glob(str(EXAMPLE_PATH) + '/*/')
#     for deck_folder in deck_folders:
#         deck_name = Path(deck_folder).name
#         tags = getDeckTags(deck_folder)
#         for tag in tags:
#             if tag not in tagMap:
#                 tagMap[tag] = set()
#             tagMap[tag].add(deck_name)

# def getDeckTags(filename):
#     file = Path(EXAMPLE_PATH, filename, 'tags.json')
#     with open(file, encoding='utf-8') as f:
#         data = json.load(f)
#         return data

tagger = Tagger()
tagger.load_tags()
tags = ['Slice Of Life', 'Kyoto Animation']
print(tagger.get_decks_by_tags(tags))
# deck = "K-On!" 
# parseDeck("{}/{}".format(category, deck))
# a = getDeckTags(deck)
# print(a)
