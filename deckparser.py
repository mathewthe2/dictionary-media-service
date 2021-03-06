import json
from pathlib import Path
from glob import glob
from tokenizer.englishtokenizer import analyze_english
from sudachipy import tokenizer
from sudachipy import dictionary
from config import EXAMPLE_PATH, LITERATURE_EXAMPLE_PATH, GAMEGENGO_PATH

tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.A

def get_deck_structure(path, filename):
    file = Path(path, filename, 'deck-structure.json')
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
        return data
    
def remove_class_from_string(s):
    if '>' in s:
        return s.split('>')[1].split('<')[0]
    else:
        return s

def parse_grammar_deck(filename):
    deck_structure = get_deck_structure(GAMEGENGO_PATH, filename)
    file = Path(GAMEGENGO_PATH, filename, 'deck.json')
    examples = []
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
        notes = data['notes']
        deck_name = data['name']
        for note in notes:
            # segmentation
            text = note['fields'][deck_structure['text-column']]
            translation = note['fields'][deck_structure['translation-column']]
            print(note['fields'][deck_structure['grammar-column']])
            grammar = remove_class_from_string(note['fields'][deck_structure['grammar-column']])
            print('parsing note', note['fields'][deck_structure['id-column']])
            example = {
                'id': note['fields'][deck_structure['id-column']],
                'deck_name': deck_name,
                'sentence': text,
                'grammar': grammar,
                'grammar_meaning': note['fields'][deck_structure['grammar-meaning-column']],
                'sentence_with_furigana': note['fields'][deck_structure['text-with-furigana-column']],
                'translation': translation,
                'timestamp': note['fields'][deck_structure['timestamp-column']],
                'image': note['fields'][deck_structure['image-column']].split('src="')[1].split('">')[0],
                'sound': note['fields'][deck_structure['sound-column']].split('sound:')[1].split(']')[0]
            }
            examples.append(example)

    with open(Path(GAMEGENGO_PATH, filename, 'data.json'), 'w+', encoding='utf8') as outfile:
        json.dump(examples, outfile, indent=4, ensure_ascii=False)

def parse_literature_deck(filename, skip_author=True):
    meta_data_file = Path(LITERATURE_EXAMPLE_PATH, filename, 'metadata.json')
    metadata = {}
    with open(meta_data_file, encoding='utf-8') as f:
        metadata = json.load(f)
    file = Path(LITERATURE_EXAMPLE_PATH, filename, 'deck.json')
    examples = []
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
        for index, entry in enumerate(data):
            if (skip_author and index == 0) or (skip_author and index == 1 and '???' in entry['sentence']):
                continue
            text = entry["sentence"]
            word_base_list = [m.normalized_form() for m in tokenizer_obj.tokenize(text, mode)]
            word_list = [m.surface() for m in tokenizer_obj.tokenize(text, mode)]
            print('name', filename)
            print('parsing note', entry["id"])
            example = {
                'id': filename + "-" + entry["id"],
                # 'author': metadata["author_english"],
                'author_japanese': metadata["author"],
                'deck_name': filename,
                'deck_name_japanese': metadata["title"],
                'sentence': text,
                'sentence_with_furigana': entry["sentence_with_furigana"],
                'word_base_list': word_base_list,
                'word_list': word_list,
                'sound': entry["id"] + '.mp3',
                'sound_begin':  entry["audio_begin"],
                'sound_end':  entry["audio_end"]
            }
            examples.append(example)

    with open(Path(LITERATURE_EXAMPLE_PATH, filename, 'data.json'), 'w+', encoding='utf8') as outfile:
        json.dump(examples, outfile, indent=4, ensure_ascii=False)

def parse_deck(filename):
    deck_structure = get_deck_structure(EXAMPLE_PATH, filename)
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
            translation_tokens = analyze_english(translation)
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

def parse_all_literature_decks():
    deck_folders = glob(str(LITERATURE_EXAMPLE_PATH) + '/*/')
    for deck_folder in deck_folders:
        parse_literature_deck(Path(deck_folder).name, skip_author=True)

def parse_all_decks():
    deck_folders = glob(str(EXAMPLE_PATH) + '/*/')
    for deck_folder in deck_folders:
        parse_deck(Path(deck_folder).name)

def print_deck_statistics():
    deck_folders = glob(str(EXAMPLE_PATH) + '/*/')
    total_notes = 0
    for deck_folder in deck_folders:
        file = Path(deck_folder, 'data.json')
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
            print('{}: {}'.format(Path(deck_folder).name, len(data)))
            total_notes += len(data)
    print("Total {} decks with {} notes".format(len(deck_folders), total_notes))

# Add data from one column in data.json to grammar.json and output to new.json
# grammar.json is a manually patched version of data.json  
def add_column_to_gamegengo(filename, column):
    file = Path(GAMEGENGO_PATH, filename, 'data.json')
    newdata = []
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
        file_to_write = Path(GAMEGENGO_PATH, filename, 'grammar.json')
        with open(file_to_write, encoding='utf-8') as f2:
            old_data = json.load(f2)
            for index, item in enumerate(old_data):
                d = item
                d[column] = data[index][column]
                newdata.append(d)

    with open(Path(GAMEGENGO_PATH, filename, 'new.json'), 'w+', encoding='utf8') as outfile:
        json.dump(newdata, outfile, indent=4, ensure_ascii=False)

# parse_grammar_deck('Game Gengo Grammar N4')
# add_column_to_gamegengo('Game Gengo Grammar N4', 'timestamp')
