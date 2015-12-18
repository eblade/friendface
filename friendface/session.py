# -*- coding: utf-8 -*-


class Session:
    def __init__(self):
        self.threads = {}  #: my thread catalog (thread id => thread)
        self.friends = {}  #: my friends, aka trusted public keys (key => alias)
        self.private_key = None  #: my global private key
        self.public_key = None  #: my global public key
        self.routes = {}  #: known peers (public key => address)

        # Networking
        self.server = None  #: our server
