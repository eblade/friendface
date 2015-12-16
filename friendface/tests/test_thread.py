# -*- coding: utf-8 -*-

from friendface import thread
from friendface.memfs import MemoryFS


def test_create_thread_should_create_folder():
    file_system = MemoryFS()
    thread_id = thread.create_thread(file_system=file_system)

    assert file_system.folder_exists(thread_id)


def test_different_threads_get_different_ids():
    file_system = MemoryFS()
    thread_id_1 = thread.create_thread(file_system=file_system)
    thread_id_2 = thread.create_thread(file_system=file_system)
    thread_id_3 = thread.create_thread(file_system=file_system)

    assert file_system.folder_exists(thread_id_1)
    assert file_system.folder_exists(thread_id_2)
    assert file_system.folder_exists(thread_id_3)

    assert thread_id_1 != thread_id_2
    assert thread_id_2 != thread_id_3
