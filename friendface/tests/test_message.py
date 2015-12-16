# -*- coding: utf-8 -*-

import pytest
import webtest
from bottle import debug

from friendface.thread import create_thread, list_thread,\
    create_message, get_message, THREAD_CONFIG
from friendface.memfs import MemoryFS


@pytest.fixture(scope='function')
def file_system():
    fs = MemoryFS()
    THREAD_CONFIG['file_system'] = fs
    return fs


@pytest.fixture(scope='function')
def thread_id(file_system):
    return create_thread()


@pytest.fixture(scope='function')
def webapp(file_system):
    from friendface.web.thread import app
    debug(True)
    return webtest.TestApp(app)


def test_create_message_should_return_an_id(thread_id, file_system):
    message = "lorem ipsum".encode('utf-8')
    message_id = create_message(thread_id, message)
    assert message_id


def test_create_message_and_get_it(thread_id, file_system):
    message = "lorem ipsum".encode('utf-8')
    message_id = create_message(thread_id, message)
    fetched = get_message(thread_id, message_id)
    assert message == fetched.get('data')


def test_create_two_messages_and_get_them(thread_id, file_system):
    message_1 = "lorem ipsum 1".encode('utf-8')
    message_2 = "lorem ipsum 2".encode('utf-8')
    message_id_1 = create_message(thread_id, message_1)
    message_id_2 = create_message(thread_id, message_2)
    fetched_1 = get_message(thread_id, message_id_1)
    fetched_2 = get_message(thread_id, message_id_2)
    assert message_1 == fetched_1.get('data')
    assert message_2 == fetched_2.get('data')
    assert message_1 != fetched_2.get('data')


def test_messages_shoud_come_back_in_order(thread_id, file_system):
    messages = ['lorem ipsum %i'.encode('utf-8') % i
                for i in range(1, 10)]
    message_ids = []
    for message in messages:
        message_ids.append(create_message(thread_id, message))
        file_system.tick()

    message_ids = tuple(message_ids)
    fetched_ids = tuple([
        t.get('name') for t in list_thread(thread_id)])

    assert message_ids == fetched_ids


def test_web_scenario(webapp, file_system):
    # Create a thread
    r = webapp.post('/')  # testing the thread application
    assert r.status_code == 201

    t = r.json
    assert t.get('type') == 'thread'
    assert t.get('id')
    assert t.get('id') in t.get('self_url')
    assert t.get('id') in t.get('message_url')

    # Create a message
    r = webapp.post(t.get('message_url'), 'hello world'.encode('utf-8'))
    assert r.status_code == 201

    m = r.json
    assert m.get('type') == 'message/reference'
    assert m.get('id')
    assert t.get('id') in m.get('self_url')
    assert m.get('id') in m.get('self_url')

    # List the thread
    r = webapp.get(t.get('self_url'))
    assert r.status_code == 200

    tl = r.json
    assert tl.get('type') == 'thread/listing'
    assert tl.get('id') == t.get('id')
    assert tl.get('self_url') == t.get('self_url')
    assert tl.get('message_url') == t.get('message_url')
    assert tl.get('message_refs')[0].get('id') == m.get('id')
    assert tl.get('message_refs')[0].get('url') == m.get('self_url')

    # Get the message
    r = webapp.get(tl.get('message_refs')[0].get('url'))
    assert r.status_code == 200

    mr = r.body.decode('utf-8')
    assert mr == 'hello world'

    # Create two more messages
    file_system.tick()
    r = webapp.post(t.get('message_url'), 'hellö wörld'.encode('utf-8'))
    assert r.status_code == 201
    m2 = r.json

    file_system.tick()
    r = webapp.post(t.get('message_url'), 'h∃llö wörld'.encode('utf-8'))
    assert r.status_code == 201
    m3 = r.json

    # List the thread again
    r = webapp.get(t.get('self_url'))
    assert r.status_code == 200

    tl = r.json
    assert tl.get('type') == 'thread/listing'
    assert tl.get('id') == t.get('id')
    assert tl.get('self_url') == t.get('self_url')
    assert tl.get('message_url') == t.get('message_url')
    assert tl.get('message_refs')[0].get('id') == m.get('id')
    assert tl.get('message_refs')[0].get('url') == m.get('self_url')
    assert tl.get('message_refs')[1].get('id') == m2.get('id')
    assert tl.get('message_refs')[1].get('url') == m2.get('self_url')
    assert tl.get('message_refs')[2].get('id') == m3.get('id')
    assert tl.get('message_refs')[2].get('url') == m3.get('self_url')

    # Get the whole thread including messages
    r = webapp.get(t.get('message_url'))
    assert r.status_code == 200

    tm = r.json
    assert tm.get('type') == 'thread/messages'
    assert tm.get('id') == t.get('id')
    assert tm.get('self_url') == t.get('message_url')
    assert tm.get('thread_url') == t.get('self_url')
    assert tm.get('messages')[0].get('id') == m.get('id')
    assert tm.get('messages')[0].get('url') == m.get('self_url')
    assert tm.get('messages')[1].get('id') == m2.get('id')
    assert tm.get('messages')[1].get('url') == m2.get('self_url')
    assert tm.get('messages')[2].get('id') == m3.get('id')
    assert tm.get('messages')[2].get('url') == m3.get('self_url')
