# -*- coding: utf-8 -*-

from bottle import redirect, request, HTTPResponse

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
        app.route('/m', 'GET', self.get_messages)
        app.route('/m', 'POST', self.register_message)
        app.route('/m/<message_id>', 'GET', self.get_message_by_id)

        app.route('/b', 'GET', self.get_branches)
        app.route('/b/<message_id>', 'GET', self.get_branch)
        app.route('/b/<message_id>', 'PUT', self.rename_branch)

    # override
    def get_thread_name(self):
        return 'internal_api'

    def get_messages(self):
        return {
            'type': 'message/list',
            'messages': list(self.session.get_message_keys()),
        }

    def register_message(self):
        body = request.body.read()
        if not body:
            return HTTPResponse('Body required', 400)

        message = Message.from_http(body, request.headers)
        message.calculate_key()
        message = sign(message)
        message.source = self.session.public_key_str
        assert message.branch is not None
        self.session.register_message(message)

        body, headers = message.to_http()

        raise HTTPResponse(
            body=body,
            status=201,
            headers=headers,
        )

    def get_message_by_id(self, message_id):
        message = self.session.get_message(message_id)
        if message is None:
            return HTTPResponse('Unknown message', 404)

        body, headers = message.to_http()

        raise HTTPResponse(
            body=body,
            status=200,
            headers=headers,
        )

    def get_branches(self):
        branches = self.session.get_branches()
        print(branches)

        return {
            'type': 'branch/listing',
            'branches': [
                {
                    'name': branch.name,
                    'root': branch.root,
                } for branch in branches
            ],
        }

    def get_branch(self, message_id):
        branch = self.session.get_branch(message_id)

        return {
            'type': 'branch',
            'name': branch.name,
            'key': branch.root,
            'messages': branch.to_flat_tree(),
        }

    def rename_branch(self, message_id):
        branch = self.session.get_branch(message_id)
        branch.name = request.body.read().decode('utf8')
        return HTTPResponse(status=200)
