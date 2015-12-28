# -*- coding: utf-8 -*-

import pytest

from friendface.session import Session
from friendface.message import Message


@pytest.fixture(scope="function")
def session():
    return Session()


def test_find_reply_of_message(session):
    replee = Message(data=b'replee')
    session.register_message(replee)

    reply = Message(data=b'reply', in_reply_to=replee.key)
    session.register_message(reply)

    branch = session.get_branch(replee.key)

    assert branch.key == replee.key
    assert len(branch) == 1
    assert reply.key in branch


def test_find_reply_of_message_two_levels_apart(session):
    replee = Message(data=b'replee')
    session.register_message(replee)

    reply = Message(data=b'reply', in_reply_to=replee.key)
    session.register_message(reply)

    reply_reply = Message(data=b'reply reply', in_reply_to=reply.key)
    session.register_message(reply_reply)

    branch = session.get_branch(replee.key)

    assert branch.key == replee.key
    assert len(branch) == 1
    assert reply.key in branch

    assert branch[reply.key].key == reply.key
    assert len(branch[reply.key]) == 1
    assert reply_reply.key in branch[reply.key]
