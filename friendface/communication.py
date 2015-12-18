# -*- coding: utf-8 -*-

import socket
import select
import threading
import logging


class Server:
    def __init__(self, hostname, port, callback, timeout=60):
        self.hostname = hostname
        self.port = port
        self.timeout = timeout
        self.server_thread = None
        self.server_socket = None
        self.callback = callback

    def start(self):
        logging.info("Preparing server at %s:%i", self.hostname, self.port)
        if self.server_thread is not None:
            raise AlreadyConnected()

        logging.info("Starting server at %s:%i", self.hostname, self.port)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((self.hostname, self.port))
            # server.setblocking(0)

            readable, _, _ = select.select([server], [], [], self.timeout)

            if len(readable) == 0:
                raise ConnectionError("Select did not return a readable server socket")

            server = readable.pop()
            self.server_socket = server
            server.listen(5)

            logging.info("Socket set up and listening at %s:%i, spawning...",
                         self.hostname, self.port)

            self.server_thread = threading.Thread(
                target=self._server,
                name="server_%s:%i" % (self.hostname, self.port),
                args=(server,),
            )
            self.server_thread.daemon = True
            self.server_thread.start()

        except Exception as e:
            logging.critical("Closing down server at %s:%i because of errors %s",
                             self.hostname, self.port, str(e))
            server.close()
            self.server_thread = None
            self.server_socket = None
            raise e
        logging.info("Server started at %s:%i", self.hostname, self.port)

    def _server(self, server):
        try:
            while True:
                logging.info("Waiting to accept...")
                (client, address) = server.accept()
                logging.info("Accepted %s", address)
                self.pickup(client, address)
        finally:
            logging.warning("Closing down server")
            server.close()
            self.server_thread = None
            self.server_socket = None

    def pickup(self, client, address):
        logging.info("Spawning pickup thread...")
        t = threading.Thread(
            target=self._client,
            name="client_%s:%i_%s" % (self.hostname, self.port, address),
            args=(client, address),
        )
        t.daemon = True
        t.start()

    def _client(self, client, address):
        logging.info("Pickup")
        readable, _, error = select.select([client], [client], [client], self.timeout)

        if len(readable) == 0:
            raise ConnectionError("Select did not return a readable client socket")
        if len(error) == 1:
            raise ConnectionError("Select did return a client socket in error")

        client = readable.pop()
        logging.info("Running callback")
        self.callback(client)
        client.close()

    def stop(self):
        logging.info("Stopping server at %s:%i", self.hostname, self.port)
        if self.server_socket is not None:
            logging.info("Closing socket at %s:%i", self.hostname, self.port)
            self.server_socket.shutdown(socket.SHUT_RDWR)
            self.server_socket.close()


class Client:
    def __init__(self, hostname, port, timeout=60):
        self.hostname = hostname
        self.port = port
        self.timeout = timeout

    def __enter__(self):
        try:
            logging.info("Connecting to %s:%i", self.hostname, self.port)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client = client
            client.connect((self.hostname, self.port))
            # client.setblocking(0)

            _, writable, error = select.select([], [client], [client], self.timeout)

            if len(writable) == 0:
                raise ConnectionError("Select did not return a writable client socket")
            if len(error) == 1:
                raise ConnectionError("Select did return a client socket in error")

            self.client = writable.pop()
            logging.info("Connected to %s:%i", self.hostname, self.port)
            return client
        except Exception as e:
            logging.info("Closing client connection to %s:%i because of error %s",
                         self.hostname, self.port, str(e))
            self.client.close()
            raise e

    def __exit__(self, type, value, traceback):
        logging.info("Closing client connection to %s:%i", self.hostname, self.port)
        self.client.close()
        logging.info("Closed client connection to %s:%i", self.hostname, self.port)


class AlreadyConnected(Exception):
    pass
