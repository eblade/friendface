# -*- coding: utf-8 -*-

import pytest
import webtest
import bottle
import os

from friendface.session import Session
from friendface.web import external
from friendface.message import Message
from friendface.privacy import get_global_keys


def get_session(name):
    session = Session()
    session.alias = name
    session.private_key, session.public_key = get_global_keys(
        os.path.join('.cache', '%s.private' % name),
        os.path.join('.cache', '%s.public' % name),
    )
    session.public_key_str = session.public_key.exportKey()
    session.friends[session.public_key_str] = session.alias
    return session


@pytest.fixture(scope="function")
def session():
    return get_session('test')


@pytest.fixture(scope='function')
def webapp(session):
    app = bottle.Bottle()
    bottle.debug(True)
    session.external_api = external.ExternalApi(session, app)
    return webtest.TestApp(app)


def test_get_message_by_id(webapp, session):
    message = Message(data=b'test')
    message.calculate_key()
    session.register_message(message)

    r = webapp.get('/m/' + message.key)
    assert r.status_code == 200
    assert r.content_type == 'text/plain'
    assert r.body == message.data


def test_get_branch_by_id(webapp, session):
    message = Message(data=b'test')
    message.calculate_key()
    session.register_message(message)

    r = webapp.get('/b/' + message.key)
    assert r.status_code == 200
    assert r.content_type == 'text/uri-list'
    assert r.body.decode() == message.key
