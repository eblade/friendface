# -*- coding: utf-8 -*-

import hashlib
import base64

from .privacy import Privacy
from .branch import Branch


class Message:
    def __init__(self, data=None, key=None, source=None, verified=False,
                 signature=None, public_key=None, private_key=None,
                 privacy=Privacy.friends, timestamp=None,
                 in_reply_to=None, content_type='text/plain', **scrap):

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
        self.content_type = content_type  #: MIME type of the message data

        # Links, run-time only
        self.branch = None  #: the Branch this message is part of

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return '<Message %s>' % (self.key or ('?'))

    @classmethod
    def from_http(self, body, headers):
        d = {key.lower().replace('-', '_'): value for key, value in headers.items()}
        if 'public_key' in d:
            d['public_key'] = base64.b64decode(d['public_key'])
        if 'signature' in d:
            d['signature'] = base64.b64decode(d['signature'])
        if 'source' in d:
            d['source'] = base64.b64decode(d['source'])
        if d.get('in_reply_to', None) == 'null':
            d['in_reply_to'] = None
        if 'privacy' in d:
            d['privacy'] = getattr(Privacy, d['privacy'])
        return Message(data=body, **d)

    def to_http(self, for_sharing=False, friends=None):

        friends = friends or {}
        source_alias = None
        if self.source and self.source in friends:
            source_alias = '@' + friends.get(self.source)

        headers = {
            'Key': self.key if self.key else None,
            'Source': base64.b64encode(self.source).decode() if self.source else None,
            'Source-Alias': source_alias,
            'Verified': 'yes' if self.verified else 'no',
            'Signature': base64.b64encode(self.signature).decode() if self.signature else None,
            'Public-Key': base64.b64encode(self.public_key).decode() if self.public_key else None,
            'Timestamp': str(self.timestamp) if self.timestamp else None,
            'In-Reply-To': self.in_reply_to if self.in_reply_to else None,
            'Content-Type': self.content_type or 'text/plain',
        }

        if not for_sharing:
            headers.update({
                'Privacy': self.privacy.name,
            })

        headers = {key: value for key, value in headers.items() if value is not None}

        return self.data, headers

    def calculate_key(self):
        if self.data is None:
            raise ValueError("Message data can't be None")

        # key should be a product of data, source, public_key, in_reply_to
        string = self.data\
            + (self.public_key.encode('utf8') if self.public_key else bytes())\
            + (self.source.encode('utf8') if self.source else bytes())\
            + (self.in_reply_to.encode('utf8') if self.in_reply_to else bytes())
        self.key = hashlib.md5(string).hexdigest()

        # create a new branch if none exists
        if self.branch is None:
            self.branch = Branch()
            self.branch.insert(self)

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
            'content_type': self.content_type,
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
        message = Message(**(self.to_dict()))
        message.branch = self.branch
        return message
