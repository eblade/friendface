# -*- coding: utf-8 -*-

import os
import pytest
import webtest
import bottle

from friendface.session import Session
from friendface.web import internal, external
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


def get_internal_app(session):
    app = bottle.Bottle()
    bottle.debug(True)
    session.internal_api = internal.InternalApi(session, app)
    return webtest.TestApp(app)


def get_external_app(session):
    app = bottle.Bottle()
    bottle.debug(True)
    session.external_api = external.ExternalApi(session, app)
    return webtest.TestApp(app)


@pytest.fixture(scope="function")
def session_a():
    return get_session('a')


@pytest.fixture(scope='function')
def int_a(session_a):
    return get_internal_app(session_a)


@pytest.fixture(scope='function')
def ext_a(session_a):
    return get_external_app(session_a)


@pytest.fixture(scope="function")
def session_b():
    return get_session('b')


@pytest.fixture(scope='function')
def int_b(session_b):
    return get_internal_app(session_b)


@pytest.fixture(scope='function')
def ext_b(session_b):
    return get_external_app(session_b)


def test_init_two_sessions_with_apps(int_a, int_b, ext_a, ext_b):
    pass


def test_message_from_a_to_b(int_a, ext_a, ext_b):
    data = b'hello world'
    r = int_a.post('/m', data, headers={'Content-Type': 'text/plain'})
    assert r.status_code == 201

    message_key = r.headers['key']
    assert message_key

    # tell b to fetch message_key from a
