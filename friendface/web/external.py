# -*- coding: utf-8 -*-

from bottle import HTTPResponse

from .api import Api
from ..privacy import sign
from ..message import Message


class ExternalApi(Api):
    def __init__(self, session, app):
        self.session = session
        self.app = app

        # Set Up External Endpoints
        app.route('/m/<message_id>', 'GET', self.get_message_by_id)
        app.route('/b/<message_id>', 'GET', self.get_branch_by_id)

    # override
    def get_thread_name(self):
        return 'external_api'

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

    def get_branch_by_id(self, message_id):
        branch = self.session.get_branch(message_id)

        if branch is None:
            return HTTPResponse('Unknown branch', 404)

        message = Message(
            data=branch.to_uri_list().encode('utf8'),
            content_type='text/uri-list')
        message = sign(
            message,
            (self.session.private_key, self.session.public_key))
        body, headers = message.to_http()

        raise HTTPResponse(
            body=body,
            status=200,
            headers=headers,
        )
