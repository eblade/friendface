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


def test_server_should_redirect_root_to_ui(webapp):
    r = webapp.get('/')
    assert r.status_code == 302
    assert r.headers.get('location').endswith('/ui')


def test_new_server_should_have_no_messages(webapp):
    r = webapp.get('/m')
    assert r.status_code == 200

    data = r.json
    assert data.get('type') == 'message/list'
    assert data.get('messages') == []


def test_new_session_should_have_no_messages(webapp):
    r = webapp.get('/m')
    assert r.status_code == 200

    data = r.json
    assert data.get('type') == 'message/list'
    assert data.get('messages') == []


def test_create_message_and_get_it_back(webapp):
    data = b'hello world'
    r = webapp.post('/m', data, headers={'Content-Type': 'text/plain'})
    assert r.status_code == 201

    message_id = r.headers['key']
    assert message_id

    r = webapp.get('/m/%s' % (message_id))
    assert message_id == r.headers['key']
    assert data == r.body


def test_create_message_should_get_signed(webapp):
    data = b'hello world'
    r = webapp.post('/m', data, headers={'Content-Type': 'text/plain'})
    message_id = r.headers['key']

    r = webapp.get('/m/%s' % (message_id))
    message = Message.from_http(r.body, r.headers)
    assert message.signature is not None
    assert message.public_key is not None

    assert verify(message)


def test_created_messages_should_end_up_in_listing(webapp):
    MESSAGE_COUNT = 3
    message_ids = set()
    for i in range(MESSAGE_COUNT):
        data = b'hello world ' + bytes(str(i), 'utf8')
        r = webapp.post('/m', data, headers={'Content-Type': 'text/plain'})
        assert r.status_code == 201
        message_ids.add(r.headers['key'])

    r = webapp.get('/m')
    assert r.status_code == 200

    assert len(message_ids) == MESSAGE_COUNT
    assert message_ids == set(r.json.get('messages'))


def test_message_should_store_reply_to(webapp):
    # First message
    r = webapp.post('/m', b'first message', headers={'Content-Type': 'text/plain'})
    first_key = r.headers['key']
    assert first_key is not None

    # Second message in reply to first message
    r = webapp.post('/m', b'reply to first message', headers={'Content-Type': 'text/plain', 'In-Reply-To': first_key})
    second_key = r.headers['key']
    in_reply_to = r.headers['in-reply-to']
    assert in_reply_to == first_key

    # Refetch reply
    r = webapp.get('/m/' + second_key)
    in_reply_to = r.headers['in-reply-to']
    assert in_reply_to == first_key
