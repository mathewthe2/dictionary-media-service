import json
import string
import zipfile
from pathlib import Path
from glob import glob
from wanakana import to_hiragana, is_japanese
from englishtokenizer import analyze_english
from japanesetokenizer import analyze_japanese, KANA_MAPPING
from config import DICTIONARY_PATH, EXAMPLE_PATH, MEDIA_FILE_HOST, EXAMPLE_LIMIT, RESULTS_LIMIT, NEW_WORDS_TO_USER_PER_SENTENCE
from tagger import Tagger
from dictionarytags import word_is_within_difficulty

example_map = {} # id to example
dictionary_map = {} # word to definition
sentence_map = {} # word to matching example ids
sentence_translation_map = {} # English word to matching example ids

tagger = Tagger()
tagger.load_tags()

def get_examples(text_is_japanese, words_map, word_bases, tags=[], user_levels={}):
    results = [words_map.get(token, set()) for token in word_bases]
    if results:
        examples = [example_map[example_id] for example_id in set.intersection(*results)]
        examples = filter_examples_by_tags(examples, tags)
        examples = filter_examples_by_level(user_levels, examples)
        examples = limit_examples(examples)
        examples = parse_examples(examples, text_is_japanese, word_bases)
        return examples
    else:
        return []

def parse_dictionary_entries(entries):
    return  [{
        'headword': entry[0],
        'reading': entry[1],
        'tags': entry[2],
        'glossary_list': entry[5],
        'sequence': entry[6],
    } for entry in entries]

def parse_examples(examples, text_is_japanese, word_bases):
    for example in examples:
        example['tags'] = tagger.get_tags_by_deck(example['deck_name'])
        example['word_index'] = []
        example['translation_word_index'] = []
        if text_is_japanese:
            example['word_index'] = [example['word_base_list'].index(word) for word in word_bases]
        else:
            example['translation_word_index'] = [example['translation_word_base_list'].index(word) for word in word_bases]
    return examples

def look_up(text, tags=[], user_levels={}):
    text_is_japanese = is_japanese(text)
    if not text_is_japanese:
        if '"' in text: # force English search
            text = text.split('"')[1]
        else:
            hiragana_text = to_hiragana(text, custom_kana_mapping=KANA_MAPPING)
            hiragana_text = hiragana_text.replace(" ", "") 
            if is_japanese(hiragana_text):
                text_is_japanese = True
                text = hiragana_text

    words_map = sentence_map if text_is_japanese else sentence_translation_map
    text = text.replace(" ", "") if text_is_japanese else text
    word_bases = analyze_japanese(text)['base_tokens'] if text_is_japanese else analyze_english(text)['base_tokens']
    examples = get_examples(text_is_japanese, words_map, word_bases, tags, user_levels)
    dictionary_words = [] if not text_is_japanese else [word for word in word_bases if word in dictionary_map]
    result = [{
        'dictionary': get_definition(text, dictionary_words),
        'examples': examples
    }]
    return dict(data=result)

def get_definition(text, dictionary_words):
    if text in dictionary_map:
        return [parse_dictionary_entries(dictionary_map[text])]
    elif dictionary_words:
        return [parse_dictionary_entries(dictionary_map[word]) for word in dictionary_words]
    else:
        return []

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
            map_sentence(example['word_base_list'], example['id'], sentence_map)
        if 'translation_word_base_list' in example:
            map_sentence(example['translation_word_base_list'], example['id'], sentence_translation_map)
        example_map[example["id"]] = example

def map_sentence(words, example_id, output_map):
    for (index, word) in enumerate(words):
        is_repeat = words.index(word) != index
        if is_repeat:
            continue
        if word in string.punctuation or word in '！？。、（）':
            continue
        if word not in output_map:
            output_map[word] = set()
        output_map[word].add(example_id)

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

def filter_examples_by_level(user_levels, examples):
    if not user_levels:
        return examples
    new_examples = []
    for example in examples:
        new_word_count = 0
        for word in example['word_base_list']:
            if word in dictionary_map:
                first_entry = dictionary_map[word][0]
                if not word_is_within_difficulty(user_levels, first_entry):
                    new_word_count += 1
        if new_word_count <= NEW_WORDS_TO_USER_PER_SENTENCE:
            new_examples.append(example)
    return new_examples

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
    return new_examples[:RESULTS_LIMIT]

def load_examples():
    deck_folders = glob(str(EXAMPLE_PATH) + '/*/')
    for deck_folder in deck_folders:
        load_example_by_path(deck_folder)

load_dictionary('JMdict+')
load_examples()