# -*- coding: utf-8 -*-

from bottle import redirect, request, HTTPResponse

from .api import Api
from .ui import ui_app, UI_CONFIG
from ..message import Message


class InternalApi(Api):
    def __init__(self, session, app, static_root='static'):
        self.session = session
        self.app = app

        # Set up User Interface
        UI_CONFIG['static_root'] = static_root
        app.mount('/ui', ui_app)
        app.route('/', 'GET', lambda: redirect('/ui'))

        # Set up internal end-points
        app.route('/thread/', 'POST', self.create_thread)
        app.route('/thread/<thread_id>/<message_id>', 'POST',
                  self.create_message)

    # override
    def get_thread_name(self):
        return 'internal_api'

    def create_thread(self):
        thread = self.session.create_thread()
        return {
            'type': 'thread',
            'id': thread.key,
        }

    def create_message(self, thread_id):
        thread = self.session.threads.get(thread_id)
        if thread is None:
            return HTTPResponse('Unknown thread', 404)

        message_data = request.json
        message = Message(message_data)
        message.calculate_key()
        thread.add_message(message)
        return message.to_dict()
