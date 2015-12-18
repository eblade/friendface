#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import argparse
import configparser


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
