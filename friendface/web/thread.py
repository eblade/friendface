# -*- coding: utf-8 -*-

from bottle import Bottle, request, response, error, HTTPResponse

from . import api
from ..thread import create_thread, list_thread, get_thread, create_message, get_message


THREAD_WEB_CONFIG = {
    'max_size': 50000,
}


app = Bottle()
api.register('thread', app)


@app.get('/<thread_id>')
def web_list_thread(thread_id):
    scheme, host, path, query_string, fragment = request.urlparts
    return {
        'type': 'thread/listing',
        'id': thread_id,
        'self_url': '%s://%s%s' % (scheme, host, path),
        'message_url': '%s://%s%s/message' % (scheme, host, path),
        'message_refs': [
            {'id': m.get('name'), 'url': '%s://%s%s/message/%s' % (scheme, host, path, m.get('name'))}
            for m in list_thread(thread_id)
        ],
    }


@app.get('/<thread_id>/message')
def web_get_thread(thread_id):
    scheme, host, path, query_string, fragment = request.urlparts
    return {
        'type': 'thread/messages',
        'id': thread_id,
        'self_url': '%s://%s%s' % (scheme, host, path),
        'thread_url': '%s://%s%s' % (scheme, host, path[:-8]),
        'messages': [
            {'id': m.get('name'), 'url': '%s://%s%s/%s' % (scheme, host, path, m.get('name')),
             'data': m.get('data')}
            for m in get_thread(thread_id, max_nr_messages=100)
        ],
    }


@app.post('/')
def web_create_thread():
    thread_id = create_thread()
    scheme, host, path, query_string, fragment = request.urlparts
    response.status = 201
    return {
        'type': 'thread',
        'id': thread_id,
        'self_url': '%s://%s%s%s' % (scheme, host, path, thread_id),
        'message_url': '%s://%s%s%s/message' % (scheme, host, path, thread_id),
    }


@app.get('/<thread_id>/message/<message_id>')
def web_get_message(thread_id, message_id):
    message = get_message(thread_id, message_id)
    return HTTPResponse(body=message.get('data'))


@app.post('/<thread_id>/message')
def web_create_message(thread_id):
    if request.content_length > THREAD_WEB_CONFIG['max_size']:
        return error(400, 'Message too large')

    data = request.body.read()
    message_id = create_message(thread_id, data)
    response.status = 201
    scheme, host, path, query_string, fragment = request.urlparts
    return {
        'type': 'message/reference',
        'id': message_id,
        'self_url': '%s://%s%s/%s' % (scheme, host, path, message_id),
    }
