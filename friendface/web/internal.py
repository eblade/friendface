# -*- coding: utf-8 -*-

from bottle import redirect, request, response, HTTPResponse

from .api import Api
from .ui import ui_app, UI_CONFIG
from ..message import Message
from ..privacy import sign


class InternalApi(Api):
    def __init__(self, session, app, static_root='static'):
        self.session = session
        self.app = app

        # Set up User Interface
        UI_CONFIG['static_root'] = static_root
        app.mount('/ui', ui_app)
        app.route('/', 'GET', lambda: redirect('/ui'))

        # Set up internal end-points
        app.route('/thread', 'GET', self.get_threads)
        app.route('/thread', 'POST', self.create_thread)
        app.route('/thread/<thread_id>', 'GET', self.get_thread_by_id)
        app.route('/thread/<thread_id>', 'POST', self.create_message)
        app.route('/thread/<thread_id>/<message_id>', 'GET', self.get_message_by_id)

    # override
    def get_thread_name(self):
        return 'internal_api'

    def get_threads(self):
        return {
            'type': 'thread/list',
            'threads': list(self.session.get_thread_keys()),
        }

    def create_thread(self):
        thread = self.session.create_thread()
        response.status = 201
        return {
            'type': 'thread',
            'id': thread.key,
            'messages': [],
        }

    def get_thread_by_id(self, thread_id):
        thread = self.session.get_thread(thread_id)
        if thread is None:
            return HTTPResponse(status_code=404)

        response.status = 200
        return {
            'type': 'thread',
            'id': thread.key,
            'messages': list(thread.get_message_keys()),
        }

    def create_message(self, thread_id):
        thread = self.session.threads.get(thread_id)
        if thread is None:
            return HTTPResponse('Unknown thread', 404)

        body = request.body.read()
        if not body:
            return HTTPResponse('Body required', 400)

        message_data = {
            'data': body,
        }

        message = Message(**message_data)
        message.calculate_key()
        message = sign(message)
        thread.add_message(message)

        body, headers = message.to_http()

        raise HTTPResponse(
            body=body,
            status=201,
            headers=headers,
        )

    def get_message_by_id(self, thread_id, message_id):
        thread = self.session.threads.get(thread_id)
        if thread is None:
            return HTTPResponse('Unknown thread', 404)

        message = thread.get_message(message_id)
        if message is None:
            return HTTPResponse('Unknown message', 404)

        body, headers = message.to_http()

        raise HTTPResponse(
            body=body,
            status=201,
            headers=headers,
        )
