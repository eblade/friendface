# -*- coding: utf-8 -*-

import pytest
import webtest
import bottle

from friendface.session import Session
from friendface.web import internal


@pytest.fixture(scope='function')
def webapp():
    app = bottle.Bottle()
    bottle.debug(True)
    session = Session()
    session.internal_api = internal.InternalApi(session, app)
    return webtest.TestApp(app)


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
