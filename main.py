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
        return look_up(request.query.keyword[:50])

@route('/anime/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root= basepath + '/resources/anime/')

run(host='localhost', port=8080)
