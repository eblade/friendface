# -*- coding: utf-8 -*-

import os
from bottle import Bottle, static_file


UI_CONFIG = {
    'static_root': 'static',
}


ui_app = Bottle()


@ui_app.get('/')
def def_get_index():
    return static_file('index.html', root=_get_static_path())


@ui_app.get('/js/<file>.js')
def get_js(file):
    return static_file(file + '.js', root=_get_static_path('js'))


@ui_app.get('/js/<file>.map')
def get_js(file):
    return static_file(file + '.map', root=_get_static_path('js'))


@ui_app.get('/css/<file>.css')
def get_css(file):
    return static_file(file + '.css', root=_get_static_path('css'))


def _get_static_path(path=None):
    static_root = UI_CONFIG.get('static_root')
    if path is None:
        return static_root
    return os.path.join(static_root, path)
