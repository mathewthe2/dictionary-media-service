from bottle import request, route, run, template, static_file, hook
from search import look_up, get_sentence_by_id
from anki import generate_deck
import os
from pathlib import Path
from config import RESOURCES_PATH

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
        user_levels = {
            'JLPT': None if not has_jlpt else int(request.query.jlpt),
            'WK': None if not has_wk else int(request.query.wk)
        }
        return look_up(
            text = request.query.keyword[:50], 
            sorting = None if not has_sorting else request.query.sort,
            tags = [] if not has_tags else request.query.tags.split(','),
            user_levels=user_levels)

@route('/anime/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root= basepath + '/resources/anime/')

@route('/download_sentence')
def download_sentence():
    sentence_id = request.query.get('id')
    if sentence_id is None:
        return 'No sentence id specified.'
    else:
        sentence = get_sentence_by_id(sentence_id)
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
