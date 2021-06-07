from dictionary import EXAMPLE_LIMIT
import json
import os
from pathlib import Path
from sudachipy import tokenizer
from sudachipy import dictionary

tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.A

bundle_path = os.path.dirname(os.path.abspath(__file__))
EXAMPLE_PATH = Path(bundle_path, 'resources', 'anime', 'Studio Ghibli')

def getDeckStructure(folder_name):
    file = Path(EXAMPLE_PATH, folder_name, 'deck-structure.json')
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
        return data

def parseDeck(folder_name):
    deck_structure = getDeckStructure(folder_name)
    file = Path(EXAMPLE_PATH, folder_name, 'deck.json')
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

            example = {
                'id': note['fields'][deck_structure['id-column']],
                'deck_name': deck_name,
                'sentence': text,
                'word_base_list': word_base_list,
                'word_list': word_list,
                'translation': note['fields'][deck_structure['translation-column']],
                'image': note['fields'][deck_structure['image-column']].split('src="')[1].split('">')[0],
                'sound': note['fields'][deck_structure['sound-column']].split('sound:')[1].split(']')[0]
            }
            examples.append(example)

    with open(Path(EXAMPLE_PATH, folder_name, 'data.json'), 'w', encoding='utf8') as outfile:
        json.dump(examples, outfile, indent=4, ensure_ascii=False)

parseDeck('Spirited Away')

# def get_base_form(word):
#     print([m.normalized_form() for m in tokenizer_obj.tokenize(word, mode)])
#     return tokenizer_obj.tokenize(word, mode)[0].dictionary_form()
#     word_base_list = [m.surface() for m in tokenizer_obj.tokenize(word, mode)]
#     return word_base_list[0]

# a = get_base_form("それとも")
# print(a)


