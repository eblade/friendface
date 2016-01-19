# -*- coding: utf-8 -*-

import os
import pytest
import webtest
import bottle
from urllib.parse import urlparse

from friendface.session import Session
from friendface.web import internal, external
from friendface.privacy import get_global_keys


class MockClient:
    def __init__(self):
        self._hosts = {}

    def register(self, hostname, app):
        self._hosts[hostname] = app

    def _do(self, method, url, *args, **kwargs):
        urlinfo = urlparse(url)
        if urlinfo.query:
            raise NotImplemented('Query part not supported "%s"' % url)
        method = getattr(self._hosts[urlinfo.netloc], method)
        return method(urlinfo.path, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        return self._do('get', url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        return self._do('put', url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self._do('post', url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        return self._do('delete', url, *args, **kwargs)


@pytest.fixture(scope="function")
def client():
    return MockClient()


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


def get_internal_app(session, client):
    app = bottle.Bottle()
    bottle.debug(True)
    session.internal_api = internal.InternalApi(session, app)
    testapp = webtest.TestApp(app)
    client.register('%s:%s' % (session.alias, 'int'), testapp)
    session.client = client
    return testapp


def get_external_app(session, client):
    app = bottle.Bottle()
    bottle.debug(True)
    session.external_api = external.ExternalApi(session, app)
    testapp = webtest.TestApp(app)
    client.register('%s:%s' % (session.alias, 'ext'), testapp)
    session.client = client
    return testapp


@pytest.fixture(scope="function")
def session_a():
    return get_session('a')


@pytest.fixture(scope='function')
def int_a(session_a, client):
    return get_internal_app(session_a, client)


@pytest.fixture(scope='function')
def ext_a(session_a, client):
    return get_external_app(session_a, client)


@pytest.fixture(scope="function")
def session_b():
    return get_session('b')


@pytest.fixture(scope='function')
def int_b(session_b, client):
    return get_internal_app(session_b, client)


@pytest.fixture(scope='function')
def ext_b(session_b, client):
    return get_external_app(session_b, client)


def test_init_two_sessions_with_apps(int_a, int_b, ext_a, ext_b):
    pass


def test_message_from_a_to_b_via_message(int_a, ext_a, session_b, int_b, ext_b):
    data = b'hello world'
    r = int_a.post('/m', data, headers={'Content-Type': 'text/plain'})
    assert r.status_code == 201

    message_key = r.headers['key']
    assert message_key

    session_b.notify('http://a:ext/m/' + message_key)

    r = int_b.get('/m/' + message_key)
    assert r.status_code == 200
    assert r.headers['Key'] == message_key


def test_message_from_a_to_b_via_branch(int_a, ext_a, session_b, int_b, ext_b):
    data = b'hello world'
    r = int_a.post('/m', data, headers={'Content-Type': 'text/plain'})
    assert r.status_code == 201

    message_key = r.headers['key']
    assert message_key

    session_b.notify('http://a:ext/b/' + message_key)

    r = int_b.get('/m/' + message_key)
    assert r.status_code == 200
    assert r.headers['Key'] == message_key
