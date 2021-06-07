from json import decoder
import json
import os
import zipfile
from pathlib import Path
from glob import glob
from bottle import abort, request
from socket import gethostname, gethostbyname 

from sudachipy import tokenizer
from sudachipy import dictionary

bundle_path = os.path.dirname(os.path.abspath(__file__))
DICTIONARY_PATH = Path(bundle_path, 'resources', 'dictionaries')
EXAMPLE_PATH = Path(bundle_path, 'resources', 'anime')
HOST = "http://localhost:8080"
EXAMPLE_LIMIT = 3
CATEGORY_LIMIT = 30

dictionary_map = {}
category_map = {}
number_of_examples_per_category_map = {}
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.A

def get_base_form(word):
    word_base_list = [m.normalized_form() for m in tokenizer_obj.tokenize(word, mode)]
    return word_base_list[0]

def parse(text):
    word_base_list = [m.normalized_form() for m in tokenizer_obj.tokenize(text, mode)]
    return word_base_list

def look_up(text, category_name='Slice Of Life'):
    text = text.replace(" ", "") 
    word_bases = parse(text)
    words = [word for word in word_bases if word in dictionary_map]
    print('category name', category_name)
    example_map = category_map[category_name]
    result = [
        {
            'dictionary': 
            [
                {
                'headword': entry[0],
                'reading': entry[1],
                'tags': entry[2],
                'glossary_list': entry[5],
                'sequence': entry[6]
                } for entry in dictionary_map[word]
            ],
            'examples': [] if word not in example_map else example_map[word]
        } for word in words]
    return dict(data=result)

def load_dictionary_by_path(dictionary_path):
    output_map = {}
    archive = zipfile.ZipFile(dictionary_path, 'r')

    result = list()
    for file in archive.namelist():
        if file.startswith('term'):
            with archive.open(file) as f:
                data = f.read()
                d = json.loads(data.decode("utf-8"))
                result.extend(d)

    for entry in result:
        if (entry[0] in output_map):
            output_map[entry[0]].append(entry)
        else:
            output_map[entry[0]] = [entry] # Using headword as key for finding the dictionary entry
    return output_map

def load_dictionary(dictionary_name):
    global dictionary_map
    dictionary_path = Path(DICTIONARY_PATH, dictionary_name + '.zip')
    if dictionary_path:
        dictionary_map = load_dictionary_by_path(str(dictionary_path))
    else:
        print('failed to find path for dictionary')

def load_example_by_path(example_path, output_map, category_name):
    examples = []
    file = Path(example_path, 'data.json')
    with open(file, encoding='utf-8') as f:
        examples = json.load(f)
    
    for example in examples:
        example = parse_example(example, category_name)
        sentence = example['sentence']
        if sentence is not None:
            words = example['word_base_list']
            for (index, word) in enumerate(words):
                is_repeat = words.index(word) != index
                if is_repeat:
                    continue
                if (word not in dictionary_map) or word in '？?!.。,()（）':
                    continue
                custom_example = example
                custom_example['word_index'] = index
                if word in output_map:
                    # if (len(output_map[word]) < EXAMPLE_LIMIT):
                    if not has_reached_example_limit_for_category(example['deck_name'], word, output_map):
                        output_map[word].append(dict(custom_example))
                else:
                    output_map[word] = [dict(custom_example)] 

    return output_map

def parse_example(example, category_name):
    # image
    image_path = '{}/anime/{}/{}/media/{}'.format(HOST, category_name, example['deck_name'], example['image'])
    example['image_url'] = image_path
    
    # sound
    sound_path = '{}/anime/{}/{}/media/{}'.format(HOST, category_name, example['deck_name'], example['sound'])
    example['sound_url'] = sound_path
    return example

def has_reached_example_limit_for_category(deck_name, word, output_map):
    if word not in output_map:
        return False
    elif len(output_map[word]) > CATEGORY_LIMIT:
        return False
    else:
        words_in_category = [example for example in output_map[word] if example['deck_name'] == deck_name]
        return len(words_in_category) >= EXAMPLE_LIMIT

def load_examples(category_name):
    global category_map
    category_map[category_name] = {}
    category_path = Path(EXAMPLE_PATH, category_name)
    deck_folders = glob(str(category_path) + '/*/')
    for deck_folder in deck_folders:
        category_map[category_name] = load_example_by_path(deck_folder, category_map[category_name], category_name)

load_dictionary('jmdict_english')
load_examples('Slice Of Life')
load_examples('Studio Ghibli')
# print(look_up('ゆめ'))