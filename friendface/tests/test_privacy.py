# -*- coding: utf-8 -*-

from friendface.privacy import sign, verify, Verification
from friendface.message import Message


def test_sign_and_verify():
    data = 'test'.encode('utf8')
    source = 'me'
    message = Message(data=data, source=source)

    message = sign(message)
    assert message.data == data
    assert message.source == source
    assert message.public_key
    assert message.private_key
    assert message.is_written_by_me()
    assert message.verified == Verification.unverified

    message = verify(message)
    assert message.data == data
    assert message.source == source
    assert message.public_key
    assert message.private_key
    assert message.is_written_by_me()
    assert message.verified == Verification.verified


def test_sign_gives_different_keys():
    num_messages = 3
    source = 'me'
    public_key = 'my public key'
    messages = []
    for i in range(num_messages):
        data = ('data ' + str(i)).encode('utf8')
        message = Message(
            data=data,
            source=source,
            public_key=public_key,
        )
        message = sign(message)
        messages.append(message)

    assert len({message.private_key for message in messages}) == num_messages
