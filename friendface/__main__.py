#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import argparse
import configparser
from bottle import Bottle, debug, redirect
from .memfs import MemoryFS
from .thread import THREAD_CONFIG

# Selecting what web API's we want to load
from .web import api
from .web import ui, thread


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage="friendface")
    parser.add_argument('-c', '--config',
                        default=os.getenv('FRIENDFACE_CONFIG', 'default.ini'),
                        help='specify what config file to run on')
    args = parser.parse_args()

    # Config
    config = configparser.ConfigParser()
    config.read(args.config)

    # Logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(threadName)s] %(filename)s +%(levelno)s %(funcName)s %(levelname)s %(message)s'
    )

    # Thread file system
    THREAD_CONFIG['file_system'] = MemoryFS()

    # Starting up the web server
    app = Bottle()
    api.mount_all(app)

    # Redirect root to ui root
    @app.get('/')
    def def_get_index():
        return redirect('/ui/')

    debug(True)
    app.run(host=config['Server']['host'], port=int(config['Server']['port']))
