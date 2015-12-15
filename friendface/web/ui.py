# -*- coding: utf-8 -*-

import os
from bottle import Bottle, static_file
from . import api


CONFIG = {
    'static_root': 'static',
}


app = Bottle()
api.register('ui', app)


@app.get('/')
def def_get_index():
    return static_file('index.html', root=_get_static_path())


@app.get('/js/<file>.js')
def get_js(file):
    return static_file(file + '.js', root=_get_static_path('js'))


@app.get('/css/<file>.css')
def get_css(file):
    return static_file(file + '.css', root=_get_static_path('css'))


def _get_static_path(path=None):
    static_root = CONFIG.get('static_root')
    if path is None:
        return static_root
    return os.path.join(static_root, path)
