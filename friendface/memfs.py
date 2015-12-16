# -*- coding: utf-8 -*-

from . import ConflictException, MissingFolderException, NotFoundException


class MemoryFS:
    def __init__(self):
        self._data = {}
        self._time = 0

    def tick(self):
        self._time += 1

    def create_folder(self, name):
        if name in self._data.keys():
            raise ConflictException()
        self._data[name] = {}

    def folder_exists(self, name):
        return name in self._data.keys()

    def get_folder(self, name):
        if not self.folder_exists(name):
            raise MissingFolderException(name)

    def ls(self, folder, max_nr=100):
        folder = self._data.get(folder)
        if folder is None:
            raise MissingFolderException(folder)

        return [
            value for value in sorted(folder.values(), key=lambda x: x.get('created'))[:max_nr]
        ]

    def store(self, folder, name, data):
        folder = self._data.get(folder)
        if folder is None:
            raise MissingFolderException(folder)

        if name in folder.keys():
            raise ConflictException()

        folder[name] = {
            'name': name,
            'data': data,
            'created': self._time,
            'modified': self._time,
        }

    def fetch(self, folder, name):
        folder = self._data.get(folder)
        if folder is None:
            raise MissingFolderException(folder)

        data = folder.get(name)
        if data is None:
            raise NotFoundException(name)

        return data
