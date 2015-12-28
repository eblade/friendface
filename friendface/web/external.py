# -*- coding: utf-8 -*-

from bottle import HTTPResponse

from .api import Api


class ExternalApi(Api):
    def __init__(self, session, app):
        self.session = session
        self.app = app

        # Set Up External Endpoints
        app.route('/<message_id>', 'GET', self.get_message)

    # override
    def get_thread_name(self):
        return 'external_api'

    def get_message(self, thread_id, message_id):
        thread = self.session.threads.get(thread_id)
        if thread is None:
            return HTTPResponse('Unknown thread', 404)

        message = thread.messages.get(message_id)
        if message is None:
            return HTTPResponse('Unknown message', 404)

        return message.to_dict(for_sharing=True)
