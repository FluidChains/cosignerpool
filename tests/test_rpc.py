import sys
sys.path.append('../src')

import unittest
import hashlib

from xmlrpc.client import ServerProxy

# start cosigner xmlrpc, bind to socket on localhost:8080
server = ServerProxy('http://127.0.0.1:8080', allow_none=True)

class TestServerAlive(unittest.TestCase):
    def test_server_alive(self):
        self.assertEqual(server.ping(), 'pong')


class TestPutGet(unittest.TestCase):
    def test_put(self):
        key = hashlib.sha224(b'xpub').hexdigest()
        value = 'Test value'
        server.put(key, value)
        self.assertEqual(server.get(key), 'Test value')

class TestDelete(unittest.TestCase):
    def test_delete(self):
        key = hashlib.sha224(b'xpub').hexdigest()
        value = 'Test value'
        server.delete(key)
        self.assertEqual(server.get(key), None)
