# -*- coding: utf-8 -*-


class Session:
    def __init__(self):
        self.messages = {}  #: my message catalog (message key => Message)
        self.friends = {}  #: my friends, trusted public keys (key => alias)
        self.private_key = None  #: my global private key
        self.public_key = None  #: my global public key
        self.public_key_str = None  #: my global public key (exported)
        self.routes = {}  #: known peers (public key => address)
        self.branches = set()  #: set of known branches

        # Networking
        self.external_app = None  #: web app for external api
        self.internal_app = None  #: web app for internal api

    def register_message(self, message):
        if message.key is None:
            message.calculate_key()

        if message.in_reply_to is not None:
            replied = self.get_message(message.in_reply_to)
            if replied is not None:
                replied.branch.insert(message)

        self.messages[message.key] = message
        self.branches.add(message.branch)

    def get_message_keys(self):
        return self.messages.keys()

    def get_message(self, key):
        return self.messages.get(key)

    def get_branch(self, key):
        message = self.get_message(key)
        return message.branch

    def get_branches(self):
        return self.branches
