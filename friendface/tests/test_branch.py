# -*- coding: utf-8 -*-

import pytest

from friendface.session import Session
from friendface.message import Message
from friendface.branch import Branch


@pytest.fixture(scope="function")
def session():
    return Session()


def test_find_reply_of_message(session):
    replee = Message(data=b'replee')
    session.register_message(replee)

    reply = Message(data=b'reply', in_reply_to=replee.key)
    session.register_message(reply)

    branch = session.get_branch(replee.key)

    assert len(branch) == 2
    assert reply.key in branch
    assert replee.key in branch
    assert branch.root == replee.key
    assert branch.replies[replee.key] == [reply.key]


def test_find_reply_of_message_two_levels_apart(session):
    replee = Message(data=b'replee')
    session.register_message(replee)

    reply = Message(data=b'reply', in_reply_to=replee.key)
    session.register_message(reply)

    reply_reply = Message(data=b'reply reply', in_reply_to=reply.key)
    session.register_message(reply_reply)

    branch = session.get_branch(replee.key)

    assert len(branch) == 3
    assert reply.key in branch
    assert replee.key in branch
    assert reply_reply.key in branch
    assert branch.root == replee.key
    assert branch.replies[replee.key] == [reply.key]
    assert branch.replies[reply.key] == [reply_reply.key]


def test_rename_branch():
    branch = Branch()
    assert branch.name is None

    branch.root = '1'
    assert branch.name == '1'

    branch.name = '2'
    assert branch.name == '2'
