# -*- coding: utf-8 -*-

import pytest
import webtest
import bottle

from friendface.session import Session
from friendface.web import external
from friendface.message import Message


@pytest.fixture(scope="function")
def session():
    return Session()


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
