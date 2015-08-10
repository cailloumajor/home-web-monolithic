# -*- coding: utf-8 -*-

from threading import Thread
from xmlrpc.server import SimpleXMLRPCServer

from django.conf import settings

from .base import BaseControler


class TestingControler(BaseControler):

    def __init__(self):
        self.output_value = 0


class TestServerThread(Thread):

    def __init__(self):
        super(TestServerThread, self).__init__()
        port = settings.PILOTWIRE_CONTROLER['port']
        self.server = SimpleXMLRPCServer(('', port), logRequests=False)
        self.server.register_instance(TestingControler())

    def run(self):
        self.server.serve_forever()

    def join(self, timeout=None):
        self.server.shutdown()
        self.server.server_close()
        super(TestServerThread, self).join(timeout)


class TestServer(object):

    def __init__(self):
        self.thread = TestServerThread()

    def __enter__(self):
        self.thread.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.thread.join()
