from bottle import request, route, run, template
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

run(host='localhost', port=8080)
