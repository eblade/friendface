#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import argparse
import configparser
from time import sleep
from bottle import Bottle

from .session import Session
from .web import external, internal
from .privacy import get_global_keys


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
        level=getattr(logging, config['logging']['level']),
        format='%(asctime)s [%(threadName)s] %(filename)s +%(levelno)s %(funcName)s %(levelname)s %(message)s',
    )

    # Session
    session = Session()
    session.alias = config['privacy']['alias']

    # Keys
    session.private_key, session.public_key = get_global_keys(
        config['privacy']['private key'],
        config['privacy']['public key'],
    )
    session.public_key_str = session.public_key.exportKey()
    session.friends[session.public_key_str] = session.alias

    # Servers
    ext_addr = config['external']['hostname'], int(config['external']['port'])
    int_addr = config['internal']['hostname'], int(config['internal']['port'])
    int_root = config['internal']['root']

    external_app = Bottle()
    session.external_api = external.ExternalApi(session, external_app)
    session.external_api.start(*ext_addr)

    internal_app = Bottle()
    session.internal_api = internal.InternalApi(session, internal_app,
                                                int_root)
    session.internal_api.start(*int_addr)

    # Main loop
    while True:
        sleep(.5)
