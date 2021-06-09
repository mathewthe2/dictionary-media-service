import json
from pathlib import Path
from englishtokenizer import analyze
from sudachipy import tokenizer
from sudachipy import dictionary
from config import EXAMPLE_PATH

tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.A

def getDeckStructure(filename):
    file = Path(EXAMPLE_PATH, filename, 'deck-structure.json')
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
        return data

def parseDeck(filename):
    deck_structure = getDeckStructure(filename)
    file = Path(EXAMPLE_PATH, filename, 'deck.json')
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

