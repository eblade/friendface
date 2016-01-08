# -*- coding: utf-8 -*-

from friendface.message import Message


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
