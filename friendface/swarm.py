# -*- coding: utf-8 -*-


class Peer:
    def __init__(self, address=None, trusted=False):
        self.address = address  #: ip or fqdn
