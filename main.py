from bottle import request, route, run, template, static_file
from dictionary import look_up

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

@route('/examples/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./resources/examples/')

run(host='localhost', port=8080)
