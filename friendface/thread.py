# -*- coding: utf-8 -*-

import hashlib
import datetime

from . import ConflictException


def create_thread(file_system):
    while True:
        try:
            ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            thread_id = hashlib.md5(ts.encode('utf8')).hexdigest()
            file_system.create_folder(thread_id)
            return thread_id
        except ConflictException:
            pass


def list_thread(thread_id, file_system):
    return file_system.ls(thread_id)


def get_thread(thread_id):
    pass


def create_message(thread_id, message, file_system):
    message_id = hashlib.md5(message.encode('utf8')).hexdigest()
    try:
        file_system.store(thread_id, message_id, message)
    except ConflictException:
        pass  # It's already saved!
    return message_id


def get_message(thread_id, message_id, file_system):
    return file_system.fetch(thread_id, message_id)
