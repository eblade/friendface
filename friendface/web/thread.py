# -*- coding: utf-8 -*-

from bottle import Bottle

from . import api
from ..thread import get_thread, get_message


app = Bottle()
api.register('thread', app)


@app.get('/<thread_id>')
def web_get_thread(thread_id):
    return get_thread(thread_id)


@app.get('/<thread_id>/<message_id>')
def web_get_message(thread_id, message_id):
    return get_message(message_id)
