# -*- coding: utf-8 -*-

from .thread import Thread


class Session:
    def __init__(self):
        self.threads = {}  #: my thread catalog (thread id => thread)
        self.friends = {}  #: my friends, trusted public keys (key => alias)
        self.private_key = None  #: my global private key
        self.public_key = None  #: my global public key
        self.routes = {}  #: known peers (public key => address)

        # Networking
        self.external_app = None  #: web app for external api
        self.internal_app = None  #: web app for internal api

    def get_thread_keys(self):
        return self.threads.keys()

    def get_thread(self, thread_id):
        return self.threads.get(thread_id)

    def create_thread(self):
        thread = Thread()
        self.threads[thread.key] = thread
        return thread
