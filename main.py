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
    category = request.query.get('category')
    tags = request.query.get('tags')
    if keyword is None:
        return 'No keyword specified.'
    else:
        return look_up(
            text=request.query.keyword[:50], 
            tags = [] if tags is None else request.query.tags.split(','),
            category_name= '' if category is None else request.query.category)

@route('/anime/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root= basepath + '/resources/anime/')

run(host='localhost', port=8080)
