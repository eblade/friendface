# -*- coding: utf-8 -*-

import threading


class Api:
    def __init__(self):
        # should set
        # * self.session (Session)
        # * self.app (Bottle app)
        raise NotImplemented

    def get_thread_name(self):
        raise NotImplemented

    def start(self, hostname, port):
        self.server_thread = threading.Thread(
            target=self._start,
            name=self.get_thread_name(),
            args=(hostname, port),
        )
        self.server_thread.daemon = True
        self.server_thread.start()

    def _start(self, hostname, port):
        self.app.run(
            hostname=hostname,
            port=port
        )
