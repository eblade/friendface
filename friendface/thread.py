# -*- coding: utf-8 -*-

import hashlib
import datetime

from .privacy import Privacy


class Thread:
    def __init__(self, key=None, seed=None, privacy=Privacy.friends):
        # TODO Better randomness
        if key:
            self._key = key
        else:
            seed = seed or\
                datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            self._key = hashlib.md5(seed.encode('utf8')).hexdigest()
        self.privacy = privacy  #: Privacy level
        self.messages = []  #: A list of messages in this Thread

    @property
    def key(self):
        """The unique key of this Thread"""
        return self._key
