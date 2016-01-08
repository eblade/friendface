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
    assert branch.root == '1'


def test_flatten_tree_with_complex_structure(session):
    a = Message(data=b'a')
    session.register_message(a)

    aa = Message(data=b'aa', in_reply_to=a.key)
    session.register_message(aa)

    ab = Message(data=b'ab', in_reply_to=a.key)
    session.register_message(ab)

    aba = Message(data=b'aba', in_reply_to=ab.key)
    session.register_message(aba)

    abaa = Message(data=b'abaa', in_reply_to=aba.key)
    session.register_message(abaa)

    #    a
    # aa   ab
    #        aba
    #        abaa

    # a
    #  aa
    # ab
    # aba
    # abaa

    branch = session.get_branch(a.key)
    tree = branch.to_flat_tree()

    for leaf in tree:
        print(' '*leaf['level'] + session.get_message(leaf['key']).data.decode('utf8'))

    assert tree == [
        {'key': a.key, 'level': 0},
        {'key': aa.key, 'level': 1},
        {'key': ab.key, 'level': 0},
        {'key': aba.key, 'level': 0},
        {'key': abaa.key, 'level': 0},
    ]


def test_flatten_tree_with_really_complex_structure(session):
    a = Message(data=b'a')
    session.register_message(a)

    aa = Message(data=b'aa', in_reply_to=a.key)
    session.register_message(aa)

    ab = Message(data=b'ab', in_reply_to=a.key)
    session.register_message(ab)

    aba = Message(data=b'aba', in_reply_to=ab.key)
    session.register_message(aba)

    abaa = Message(data=b'abaa', in_reply_to=aba.key)
    session.register_message(abaa)

    ac = Message(data=b'ac', in_reply_to=a.key)
    session.register_message(ac)

    aca = Message(data=b'aca', in_reply_to=ac.key)
    session.register_message(aca)

    acaa = Message(data=b'acaa', in_reply_to=aca.key)
    session.register_message(acaa)

    acaaa = Message(data=b'acaaa', in_reply_to=acaa.key)
    session.register_message(acaaa)

    acaab = Message(data=b'acaab', in_reply_to=acaa.key)
    session.register_message(acaab)

    acaaba = Message(data=b'acaaba', in_reply_to=acaab.key)
    session.register_message(acaaba)

    #    a
    # aa   ab      ac
    #        aba    acaa
    #        abaa  acaaa  acaab
    #                       acaaba

    # a
    #  aa
    #  ab
    #  aba
    #  abaa
    # ac
    # aca
    # acaa
    #  acaaa
    # acaab
    # acaaba

    branch = session.get_branch(a.key)
    tree = branch.to_flat_tree()

    for leaf in tree:
        print(' '*leaf['level'] + session.get_message(leaf['key']).data.decode('utf8'))

    assert tree == [
        {'key': a.key, 'level': 0},
        {'key': aa.key, 'level': 1},
        {'key': ab.key, 'level': 1},
        {'key': aba.key, 'level': 1},
        {'key': abaa.key, 'level': 1},
        {'key': ac.key, 'level': 0},
        {'key': aca.key, 'level': 0},
        {'key': acaa.key, 'level': 0},
        {'key': acaaa.key, 'level': 1},
        {'key': acaab.key, 'level': 0},
        {'key': acaaba.key, 'level': 0},
    ]
