# -*- coding: utf-8 -*-

import pytest
import webtest
import bottle

from friendface.session import Session
from friendface.web import internal
from friendface.privacy import verify
from friendface.message import Message


@pytest.fixture(scope="function")
def session():
    return Session()


@pytest.fixture(scope='function')
def webapp(session):
    app = bottle.Bottle()
    bottle.debug(True)
    session.internal_api = internal.InternalApi(session, app)
    return webtest.TestApp(app)


@pytest.fixture(scope='function')
def thread(session):
    return session.create_thread()


def test_server_should_redirect_root_to_ui(webapp):
    r = webapp.get('/')
    assert r.status_code == 302
    assert r.headers.get('location').endswith('/ui')


def test_new_server_should_have_no_threads(webapp):
    r = webapp.get('/thread')
    assert r.status_code == 200

    data = r.json
    assert data.get('type') == 'thread/list'
    assert data.get('threads') == []


def test_create_thread_and_get_it_back(webapp):
    r = webapp.post('/thread')
    assert r.status_code == 201

    data = r.json
    assert data.get('type') == 'thread'
    assert data.get('id') is not None

    r = webapp.get('/thread/' + data.get('id'))
    assert r.status_code == 200


def test_new_thread_should_be_listed(webapp, thread):
    r = webapp.get('/thread')
    assert r.status_code == 200

    data = r.json
    assert data.get('type') == 'thread/list'
    assert data.get('threads') == [thread.key]


def test_new_thread_should_have_no_messages(webapp, thread):
    r = webapp.get('/thread/' + thread.key)
    assert r.status_code == 200

    data = r.json
    assert data.get('type') == 'thread'
    assert data.get('messages') == []


def test_create_message_and_get_it_back(webapp, thread):
    data = b'hello world'
    r = webapp.post('/thread/' + thread.key, data, headers={'Content-Type': 'text/plain'})
    assert r.status_code == 201

    message_id = r.headers['key']
    assert message_id

    r = webapp.get('/thread/%s/%s' % (thread.key, message_id))
    assert message_id == r.headers['key']
    assert data == r.body


def test_create_message_should_get_signed(webapp, thread):
    data = b'hello world'
    r = webapp.post('/thread/' + thread.key, data, headers={'Content-Type': 'text/plain'})
    message_id = r.headers['key']

    r = webapp.get('/thread/%s/%s' % (thread.key, message_id))
    message = Message.from_http(r.body, r.headers)
    assert message.signature is not None
    assert message.public_key is not None

    assert verify(message)
