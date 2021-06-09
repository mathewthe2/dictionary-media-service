import json
import re
import string
import zipfile
from pathlib import Path
from glob import glob
from englishtokenizer import analyze
from config import DICTIONARY_PATH, EXAMPLE_PATH, MEDIA_FILE_HOST, EXAMPLE_LIMIT, CATEGORY_LIMIT
from tagger import Tagger

from sudachipy import tokenizer
from sudachipy import dictionary

example_map = {}
dictionary_map = {}
sentence_map = {}
sentence_translation_map = {}
number_of_examples_per_category_map = {}
tagger = Tagger()
tagger.load_tags()

tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.A

def get_base_form(word):
    word_base_list = [m.normalized_form() for m in tokenizer_obj.tokenize(word, mode)]
    return word_base_list[0]

def parse(text):
    word_base_list = [m.normalized_form() for m in tokenizer_obj.tokenize(text, mode)]
    return word_base_list

def is_alphaneumeric(text):
    return re.search('[a-zA-Z]', text) is not None

def english_look_up(text, tags=[], category_name='Slice Of Life'):
    word_bases = analyze(text)['base_tokens']
    results =  [sentence_translation_map.get(token, set()) for token in word_bases]
    if results:
        examples = [example_map[example_id] for example_id in set.intersection(*results)]
        examples = filter_examples_by_tags(examples, tags)
        examples = limit_examples(examples)
        return dict(data=[{
            'dictionary': [],
            'examples':examples
         },])
    else:
        return []


def look_up(text, tags=[], category_name='anime'):
    if (is_alphaneumeric(text)):
        return english_look_up(text, tags, category_name)
    text = text.replace(" ", "") 
    word_bases = parse(text)
    words = [word for word in word_bases if word in dictionary_map]
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
            'examples': [] if word not in sentence_map else sentence_map[word]
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

def load_example_by_path(example_path):
    global sentence_map
    global sentence_translation_map
    examples = []
    file = Path(example_path, 'data.json')
    with open(file, encoding='utf-8') as f:
        examples = json.load(f)
    
    for example in examples:
        example = parse_example(example)
        if 'word_base_list' in example:
            map_japanese_sentence(example, sentence_map)
        if 'translation_word_base_list' in example:
            map_english_sentence(example, sentence_translation_map)
        example_map[example["id"]] = example

def map_japanese_sentence(example, output_map):
    words = example['word_base_list']
    for (index, word) in enumerate(words):
        is_repeat = words.index(word) != index
        if is_repeat:
            continue
        if word in string.punctuation:
            continue
        custom_example = example
        custom_example['word_index'] = index
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

def map_english_sentence(example, output_map):
    words = example['translation_word_base_list']
    for (index, word) in enumerate(words):
        is_repeat = words.index(word) != index
        if is_repeat:
            continue
        if word in string.punctuation:
            continue
        custom_example = example
        custom_example['translated_word_index'] = index
        if word not in output_map:
            output_map[word] = set()
        output_map[word].add(custom_example["id"])

def parse_example(example):
    # image
    image_path = '{}/anime/{}/media/{}'.format(MEDIA_FILE_HOST, example['deck_name'], example['image'])
    example['image_url'] = image_path
    
    # sound
    sound_path = '{}/anime/{}/media/{}'.format(MEDIA_FILE_HOST, example['deck_name'], example['sound'])
    example['sound_url'] = sound_path
    return example

def filter_examples_by_tags(examples, tags):
    if len(tags) <= 0:
        return examples
    deck_names = tagger.get_decks_by_tags(tags)
    return [example for example in examples if example['deck_name'] in deck_names]

def limit_examples(examples):
    example_count_map = {}
    new_examples = []
    for example in examples:
        deck_name = example['deck_name']
        if deck_name not in example_count_map:
            example_count_map[deck_name] = 0
        example_count_map[deck_name] += 1
        if (example_count_map[deck_name] <= EXAMPLE_LIMIT):
            new_examples.append(example)
    return new_examples

def has_reached_example_limit_for_category(deck_name, word, output_map):
    if word not in output_map:
        return False
    elif len(output_map[word]) > CATEGORY_LIMIT:
        return False
    else:
        words_in_category = [example for example in output_map[word] if example['deck_name'] == deck_name]
        return len(words_in_category) >= EXAMPLE_LIMIT

def load_examples():
    deck_folders = glob(str(EXAMPLE_PATH) + '/*/')
    for deck_folder in deck_folders:
        load_example_by_path(deck_folder)

load_dictionary('jmdict_english')
load_examples()
# print('finished loading')
# a = look_up('love', tags=["Music"])['data'][0]['examples']
# print(a)
# print(len(a))