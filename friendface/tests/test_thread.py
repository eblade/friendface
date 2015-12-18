# -*- coding: utf-8 -*-

import pytest

from friendface.thread import Thread
from friendface.storage import Storage


@pytest.fixture(scope="function")
def storage():
    return Storage()


def test_created_thread_should_have_key():
    thread = Thread(seed='0')
    assert thread.key is not None


def test_created_thread_should_have_no_messages():
    thread = Thread(seed='0')
    assert len(thread.messages) == 0


def test_different_threads_get_different_ids():
    threads = [Thread(seed=str(x)) for x in range(10)]
    keys = set(thread.key for thread in threads)
    assert len(keys) == len(threads)
