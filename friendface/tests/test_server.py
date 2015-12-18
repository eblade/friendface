# -*- coding: utf-8 -*-

import pytest
import logging

from friendface.communication import Server, Client


LOCALHOST = 'localhost'
FORMAT = '%(asctime)s [%(threadName)s] %(filename)s +%(levelno)s %(funcName)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)


@pytest.fixture(scope="session")
def port():
    return 9998


def test_server_startup(port):
    def handler(socket):
        pass
    server = Server(LOCALHOST, port, handler)
    server.start()
    server.stop()


def test_echo(port):
    message = 'hello'.encode('utf8')

    def echo(socket):
        socket.send(socket.recv(1024))

    server = Server(LOCALHOST, port, echo)
    server.start()

    with Client(LOCALHOST, port) as client:
        client.send(message)
        echoed = client.recv(1024)

    server.stop()

    assert echoed == message
