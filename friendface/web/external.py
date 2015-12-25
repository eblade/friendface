# -*- coding: utf-8 -*-

from bottle import request, HTTPResponse

from .api import Api


class ExternalApi(Api):
    def __init__(self, session, app):
        self.session = session
        self.app = app

        # Set Up External Endpoints
        app.route('/<thread_id>', 'GET', self.get_message_ids_in_thread)
        app.route('/<thread_id>', 'PUT', self.bulk_get_messages_in_thread)
        app.route('/<thread_id>/<message_id>', 'GET', self.get_message)

    # override
    def get_thread_name(self):
        return 'external_api'

    def get_message_ids_in_thread(self, thread_id):
        thread = self.session.threads.get(thread_id)
        if thread is None:
            return HTTPResponse('Unknown thread', 404)

        return {
            'type': 'thread/listing',
            'id': thread_id,
            'messages': thread.messages.keys(),
        }

    def bulk_get_messages_in_thread(self, thread_id):
        thread = self.session.threads.get(thread_id)
        if thread is None:
            return HTTPResponse('Unknown thread', 404)

        asked_for = request.json.get('messages')

        return {
            'type': 'thread/messages',
            'id': thread_id,
            'messages': {
                message.key: message.to_dict(for_sharing=True)
                for key, message in thread.message.items()
                if key in asked_for
            },
        }

    def get_message(self, thread_id, message_id):
        thread = self.session.threads.get(thread_id)
        if thread is None:
            return HTTPResponse('Unknown thread', 404)

        message = thread.messages.get(message_id)
        if message is None:
            return HTTPResponse('Unknown message', 404)

        return message.to_dict(for_sharing=True)
