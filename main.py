from bottle import request, route, run, template, static_file
from dictionary import look_up
import os

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
        tags = request.query.get('tags')
        user_levels = {
            'JLPT': None if request.query.get('jlpt') is None else request.query.jlpt,
            'WK': None if request.query.get('wk') is None else request.query.wk
        }
        return look_up(
            text=request.query.keyword[:50], 
            tags = [] if tags is None else request.query.tags.split(','),
            user_levels=user_levels)

@route('/anime/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root= basepath + '/resources/anime/')

run(host='localhost', port=8080)
