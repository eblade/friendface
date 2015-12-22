# -*- coding: utf-8 -*-

import pytest

from friendface.thread import Thread
from friendface.message import Message


@pytest.fixture(scope="function")
def seed():
    def iterator():
        x = 0
        while True:
            yield str(x)
            x += 1
    return iterator()


@pytest.fixture(scope="function")
def thread(seed):
    return Thread(seed=next(seed))


def test_message_generate_key():
    data = 'test'.encode('utf8')
    public_key = 'public key'
    message = Message(data=data, public_key=public_key)
    assert message.data == data
    assert message.public_key == public_key
    message.calculate_key()
    assert message.data == data
    assert message.public_key == public_key
    assert message.key is not None


def test_messages_in_a_thread(thread):
    num_messages = 10
    last_key = None
    source = 'me'
    public_key = 'my public key'
    for i in range(num_messages):
        data = ('data ' + str(i)).encode('utf8')
        message = Message(
            data=data,
            source=source,
            public_key=public_key,
            in_reply_to=last_key,
        )
        message.calculate_key()
        last_key = message.key
        thread.messages[message.key] = message

    assert len(thread.messages) == num_messages
