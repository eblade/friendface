# -*- coding: utf-8 -*-

import hashlib

from .privacy import Privacy


class Message:
    def __init__(self, data=None, key=None, source=None, verified=False,
                 signature=None, public_key=None, private_key=None,
                 privacy=Privacy.friends, timestamp=None,
                 in_reply_to=None):

        self.data = data  #: The actual data, as a byte string
        self.key = key  #: The hash key for this message
        self.source = source  #: The global public key of the source of the message
        self.verified = verified  #: Whether or not the source is verified
        self.signature = signature  #: Signature of the message
        self.public_key = public_key  #: The public key for this message
        self.private_key = private_key  #: Your private key for this message
        self.privacy = privacy  #: Verification level
        self.timestamp = timestamp  #: non-trusted timestamp (unix epoch)
        self.in_reply_to = in_reply_to  #: key of a message in the same thread

    def calculate_key(self):
        if self.data is None:
            raise ValueError("message can't be None")
        if self.public_key is None:
            raise ValueError("public_key can't be None")

        # key should be a product of data, source, public_key, in_reply_to
        string = self.data\
            + self.public_key.encode('utf8')\
            + (self.source.encode('utf8') if self.source else bytes())\
            + (self.in_reply_to.encode('utf8') if self.in_reply_to else bytes())
        self.key = hashlib.md5(string).hexdigest()

    def to_dict(self, for_sharing=False):
        d = {
            'data': self.data,
            'key': self.key,
            'source': self.source,
            'verified': self.verified,
            'signature': self.signature,
            'public_key': self.public_key,
            'timestamp': self.timestamp,
            'in_reply_to': self.in_reply_to,
        }

        if not for_sharing:
            d.update({
                'private_key': self.private_key,
                'privacy': self.privacy,
            })

        return d

    def is_written_by_me(self):
        return self.private_key is not None

    def copy(self):
        """
        Perform a shallow copy of the message.
        """
        return Message(**(self.to_dict()))
