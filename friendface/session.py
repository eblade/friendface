# -*- coding: utf-8 -*-


import requests
from urllib.parse import urlparse, urlunparse
from .message import Message


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
        self.client = requests.Session()  #: web client

    def register_message(self, message):
        if message.key is None:
            message.calculate_key()

        if message.in_reply_to is not None:
            replied = self.get_message(message.in_reply_to)
            if replied is not None:
                replied.branch.insert(message)
            else:
                pass  # FIXME Loose end! Must remember this!

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

    def notify(self, address):
        r = self.client.get(address)
        if r.content_type == 'text/uri-list':
            keys = r.body.split(b'\n')
            urlinfo = list(urlparse(address))
            for key in keys:
                if key not in self.messages.keys():
                    urlinfo[2] = '/m/' + key.decode('utf8')
                    print(urlinfo)
                    self.notify(urlunparse(urlinfo))
        else:
            message = Message.from_http(r.body, r.headers)
            self.register_message(message)
