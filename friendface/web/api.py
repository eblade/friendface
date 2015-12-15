# -*- coding: utf-8 -*-

"""
Collects and mounts bottle apps on a given root app. Run register from each
sub-api and then call mount_all with the root app.
"""

import logging

_apis = {}
_local = {}


def register(mount_point, app):
    if _local.get('locked') is True:
        raise Exception("API regitration is locked")
    if mount_point in _apis.keys():
        raise NameError("API already mounted on '%s'" % mount_point)

    _apis[mount_point] = app


def mount_all(root_app):
    _local['locked'] = True
    for mount_point, app in _apis.items():
        logging.info("Mounting app on '%s'", mount_point)
        root_app.mount(mount_point, app)
