from bottle import request, response, route, run, template, static_file, hook
from search import get_deck_by_id, look_up, get_sentence_by_id, get_sentence_with_context, get_sentences_with_combinatory_ids
from anki import generate_deck
import requests
import os
from pathlib import Path
from config import RESOURCES_PATH, DEFAULT_CATEGORY, MEDIA_FILE_HOST

basepath = os.path.abspath(".")

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

@route('/look_up_dictionary')
def look_up_dictionary():
    keyword = request.query.get('keyword')
    if keyword is None:
        return 'No keyword specified.'
    else:
        has_tags = request.query.get('tags') is not None and request.query.get('tags') != ''
        has_jlpt = request.query.get('jlpt') is not None and request.query.get('jlpt') != ''
        has_wk = request.query.get('wk') is not None and request.query.get('wk') != ''
        has_sorting = request.query.get('sort') is not None and request.query.get('sort') != ''
        has_category = request.query.get('category') is not None and request.query.get('category') != ''
        user_levels = {
            'JLPT': None if not has_jlpt else int(request.query.jlpt),
            'WK': None if not has_wk else int(request.query.wk)
        }
        response.set_header('Access-Control-Allow-Origin', '*')
        response.add_header('Access-Control-Allow-Methods', 'GET')
        return look_up(
            text = request.query.keyword[:50], 
            sorting = None if not has_sorting else request.query.sort,
            category = DEFAULT_CATEGORY if not has_category else request.query.category,
            tags = [] if not has_tags else request.query.tags.split(','),
            user_levels=user_levels)

@route('/sentence_with_context')
def sentence_with_context():
    sentence_id = request.query.get('id')
    has_category = request.query.get('category') is not None and request.query.get('category') != ''
    response.set_header('Access-Control-Allow-Origin', '*')
    response.add_header('Access-Control-Allow-Methods', 'GET')
    if sentence_id is None:
        return 'No sentence id specified.'
    else: 
        return get_sentence_with_context(request.query.id, category=DEFAULT_CATEGORY if not has_category else request.query.category)

@route('/deck')
def deck():
    deck_id = request.query.get('id')
    has_category = request.query.get('category') is not None and request.query.get('category') != ''
    if deck_id is None:
        return 'No idspecified.'
    else: 
        response.set_header('Access-Control-Allow-Origin', '*')
        response.add_header('Access-Control-Allow-Methods', 'GET')
        return get_deck_by_id(request.query.id, category=DEFAULT_CATEGORY if not has_category else request.query.category)

@route('/sentences')
def sentences():
    sentences_ids = request.query.get('ids')
    if sentences_ids is None:
        return 'No sentence ids specified.'
    else: 
        response.set_header('Access-Control-Allow-Origin', '*')
        response.add_header('Access-Control-Allow-Methods', 'GET')
        return get_sentences_with_combinatory_ids(request.query.ids.split(','))


@route('/anime/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root= basepath + '/resources/anime/')

# Download static files from Digital Ocean bucket
@route('/download_media')
def download_media():
    path = request.query.get('path')
    if path is None:
        return 'No path specified.'
    else:
        response = requests.get(MEDIA_FILE_HOST + '/' + path)
        name = path.rsplit('/', 1)[1]
        file_name = Path(RESOURCES_PATH, "static", name)
        file = open(file_name, "wb")
        file.write(response.content)
        file.close()
        @hook('after_request')
        def deleteFile():
            file =  Path(RESOURCES_PATH, 'static', name)
            if os.path.exists(file):
                os.remove(file)
        return static_file(name, root= str(Path(RESOURCES_PATH, 'static')), download=name)

@route('/download_sentence_audio')
def download_sentence_audio():
    sentence_id = request.query.get('id')
    if sentence_id is None:
        return 'No sentence id specified.'
    else:
        has_category = request.query.get('category') is not None and request.query.get('category') != ''
        sentence = get_sentence_by_id(sentence_id, category=DEFAULT_CATEGORY if not has_category else request.query.category)
        if sentence is None:
            return 'File not found.'
        else:
            # Download Sound
            response = requests.get(sentence["sound_url"])
            sound_file_name = Path(RESOURCES_PATH, "sound", sentence["sound"])
            file = open(sound_file_name, "wb")
            file.write(response.content)
            file.close()
            @hook('after_request')
            def deleteFile():
                file =  Path(RESOURCES_PATH, 'sound', sentence["sound"])
                if os.path.exists(file):
                    os.remove(file)
            return static_file(sentence["sound"], root= str(Path(RESOURCES_PATH, 'sound')), download=sentence["sound"])

@route('/download_sentence_image')
def download_sentence_image():
    sentence_id = request.query.get('id')
    if sentence_id is None:
        return 'No sentence id specified.'
    else:
        has_category = request.query.get('category') is not None and request.query.get('category') != ''
        sentence = get_sentence_by_id(sentence_id, category=DEFAULT_CATEGORY if not has_category else request.query.category)
        if sentence is None:
            return 'File not found.'
        else:
            response = requests.get(sentence["image_url"])
            image_file_name = Path(RESOURCES_PATH, "images", sentence["image"])
            file = open(image_file_name, "wb")
            file.write(response.content)
            file.close()
            @hook('after_request')
            def deleteFile():
                file =  Path(RESOURCES_PATH, 'images', sentence["image"])
                if os.path.exists(file):
                    os.remove(file)
            return static_file(sentence["image"], root= str(Path(RESOURCES_PATH, 'images')), download=sentence["image"])

@route('/download_sentence')
def download_sentence_apkg():
    sentence_id = request.query.get('id')
    if sentence_id is None:
        return 'No sentence id specified.'
    else:
        has_category = request.query.get('category') is not None and request.query.get('category') != ''
        sentence = get_sentence_by_id(sentence_id, category=DEFAULT_CATEGORY if not has_category else request.query.category)
        if sentence is None:
            return 'File not found.'
        else:
            deck = generate_deck(sentence)
            @hook('after_request')
            def deleteDeck():
                file =  Path(RESOURCES_PATH, 'decks', deck)
                if os.path.exists(file):
                    os.remove(file)
            return static_file(deck, root= str(Path(RESOURCES_PATH, 'decks')), download=deck)


run(host='localhost', port=8080)
