# -*- coding: utf-8 -*-


import pytest

from friendface.thread import create_thread, list_thread,\
    create_message, get_message
from friendface.memfs import MemoryFS


@pytest.fixture(scope='function')
def file_system():
    return MemoryFS()


@pytest.fixture(scope='function')
def thread_id(file_system):
    return create_thread(file_system)


def test_create_message_should_return_an_id(thread_id, file_system):
    message = "lorem ipsum"
    message_id = create_message(thread_id, message, file_system)
    assert message_id


def test_create_message_and_get_it(thread_id, file_system):
    message = "lorem ipsum"
    message_id = create_message(thread_id, message, file_system)
    fetched = get_message(thread_id, message_id, file_system)
    assert message == fetched


def test_create_two_messages_and_get_them(thread_id, file_system):
    message_1 = "lorem ipsum 1"
    message_2 = "lorem ipsum 2"
    message_id_1 = create_message(thread_id, message_1, file_system)
    message_id_2 = create_message(thread_id, message_2, file_system)
    fetched_1 = get_message(thread_id, message_id_1, file_system)
    fetched_2 = get_message(thread_id, message_id_2, file_system)
    assert message_1 == fetched_1
    assert message_2 == fetched_2
    assert message_1 != fetched_2


def test_messages_shoud_come_back_in_order(thread_id, file_system):
    messages = ['lorem ipsum %i' % i for i in range(1,10)]
    message_ids = []
    for message in messages:
        message_ids.append(create_message(
            thread_id, message, file_system))

    message_ids = tuple(message_ids)
    fetched_ids = tuple([
        t.get('name') for t in list_thread(thread_id, file_system)])

    assert message_ids == fetched_ids
