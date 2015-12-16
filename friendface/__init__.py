# -*- coding: utf-8 -*-
"""
friendface is the webapp. see __main__.py
"""

import sys

assert sys.version_info > (3, 5, 1)  # We will require 3.5 at some point


class ConflictException(Exception):
    pass


class MissingFolderException(Exception):
    def __init__(self, folder):
        super().__init__('The folder "%s" does not exist' % folder)


class NotFoundException(Exception):
    def __init__(self, name):
        super().__init__('The object "%s" does not exist' % name)
