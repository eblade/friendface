# -*- coding: utf-8 -*-

import hashlib
import datetime

from . import ConflictException



THREAD_CONFIG = {
    'file_system': None,
}


class Thread:
    def __init__(self):
        # TODO Better randomness
        ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        self._key = hashlib.md5(ts.encode('utf8')).hexdigest()
        self.messages = []

    @property
    def key(self):
        return self._key


class Message:
    def __init__(self, data):
        self.data = data  # The actual data, as a unicode string
        self.key = None  # The hash key for this message
        self.source = None  # The global public key of the source of the message
        self.public_key = None  # The public key for this message
        self.private_key = None  # Your private key for this message
        self.deny = False  # True if you will verify this
        self.timestamp = None  # non-trusted timestamp (unix epoch)
        self.in_reply_to = None  # key of a message in the same thread

    def calculate_key(self):
        if self.data is None:
            raise ValueError("message can't be None")
        if self.source is None:
            raise ValueError("source can't be None")
        if self.public_key is None:
            raise ValueError("public_key can't be None")
        
        # key should be a product of data, source, public_key, in_reply_to
        string = self.data + self.public_key + self.source + (self.in_reply_to or '')
        self.key = hashlib.md5(string.encode('utf8').hexdigest()
    
    def to_dict(self, for_sharing=False, for_key=False):
        if self.key is None:
            self.calculate_key()

        d = {
            'data': self.data,
            'key': self.key,
            'source': self.source,
            'public_key': self.public_key,
            'timestamp': self.timestamp,
            'in_reply_to': self.in_reply_to,
        }

        if not for_sharing:
            d.update({
                'private_key': self.private_key,
                'deny': self.deny,
            })

        return d

    @classmethod
    def from_dict(self, d):
        m = Message()
        m.data = d.get('data')
        m.key = d.get('key')
        m.source = d.get('source')
        m.public_key = d.get('public_key')
        m.private_key = d.get('private_key')
        m.deny = d.get('deny', False)
        m.timestamp = d.get('timestamp')
        m.in_reply_to = d.get('in_reply_to')

        if m.key is None:
            m.calculate_key()

        return m

    def is_written_by_me(self):
        return self.private_key is not None


def create_thread(file_system=None):
    file_system = file_system or THREAD_CONFIG['file_system']
    while True:
        try:
            ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            thread_id = hashlib.md5(ts.encode('utf8')).hexdigest()
            file_system.create_folder(thread_id)
            return thread_id
        except ConflictException:
            pass


def list_thread(thread_id, file_system=None):
    file_system = file_system or THREAD_CONFIG['file_system']
    return file_system.ls(thread_id)


def get_thread(thread_id, max_nr_messages=100, file_system=None):
    file_system = file_system or THREAD_CONFIG['file_system']
    tl = file_system.ls(thread_id, max_nr=max_nr_messages)
    for message in tl:
        message['data'] = get_message(thread_id, message.get('name'))\
                          .get('data').decode('utf8')
    return tl


def create_message(thread_id, message, file_system=None):
    file_system = file_system or THREAD_CONFIG['file_system']
    assert isinstance(message, bytes)
    message_id = hashlib.md5(message).hexdigest()
    try:
        file_system.store(thread_id, message_id, message)
    except ConflictException:
        pass  # It's already saved!
    return message_id


def get_message(thread_id, message_id, file_system=None):
    file_system = file_system or THREAD_CONFIG['file_system']
    return file_system.fetch(thread_id, message_id)
