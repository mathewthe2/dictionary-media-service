from json import decoder
import json
import os
import zipfile
from fugashi import Tagger
from pathlib import Path
from bottle import abort, request
from socket import gethostname, gethostbyname 

bundle_path = os.path.dirname(os.path.abspath(__file__))
DICTIONARY_PATH = Path(bundle_path, 'resources', 'dictionaries')
EXAMPLE_PATH = Path(bundle_path, 'resources', 'anime')
HOST = "http://localhost:8080"
EXAMPLE_LIMIT = 3

dictionary_map = {}
example_map = {}

def parse(text):
    tagger = Tagger('-Owakati')
    tagger.parse(text)
    word_base_list = [word.feature.lemma for word in tagger(text)]
    return word_base_list

def look_up(text):
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

def load_example_by_path(example_path):
    notes = []
    deck_name = ''
    file = Path(example_path, 'deck.json')
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
        notes = data['notes']
        deck_name = data['name']
    
    output_map = {}
    print('notes', len(notes))
    for note in notes:
        note = parse_note(note, deck_name)
        sentence = note['fields'][1]
        if sentence is not None:
            words = note['word_base_list']
            for (index, word) in enumerate(words):
                if (word not in dictionary_map) or word in '？?!.,':
                    continue
                custom_note = note
                custom_note['word_index'] = index
                if word in output_map:
                    if (len(output_map[word]) < EXAMPLE_LIMIT):
                        output_map[word].append(dict(custom_note))
                else:
                    output_map[word] = [dict(custom_note)] 
    return output_map

def parse_note(note, deck_name):
    # tagging
    text = note['fields'][1]
    tagger = Tagger('-Owakati')
    tagger.parse(text)
    note['word_base_list'] = [word.feature.lemma for word in tagger(text)]
    note['word_list'] = [str(word) for word in tagger(text)]

    # image
    image_value = note['fields'][7]
    image_name = image_value.split('src="')[1].split('">')[0]
    image_path = '{}/anime/{}/media/{}'.format(HOST, deck_name, image_name)
    note['image_url'] = image_path
    
    # sound
    sound_value = note['fields'][8]
    sound_name = sound_value.split('sound:')[1].split(']')[0]
    sound_path = '{}/anime/{}/media/{}'.format(HOST, deck_name, sound_name)
    note['sound_url'] = sound_path
    return note

def load_examples(media_name):
    global example_map
    example_path = Path(EXAMPLE_PATH, media_name)
    if example_path:
        example_map = load_example_by_path(str(example_path))
    else:
        print('failed to find path for examples')

load_dictionary('jmdict_english')
load_examples('Anime - Your Name')