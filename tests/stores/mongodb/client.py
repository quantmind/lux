from pulsar import new_event_loop
from pulsar.apps.test import unittest
from pulsar.apps.data import create_store


try:
    import pymongo
    client = pymongo.MongoClient()
    alive = client.alive()
except Exception:
    alive = False


@unittest.skipUnless(alive, "Requires pymongo and a running mongodb")
class TestMongoDb(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.store = cls.create_store(loop=new_event_loop())

    @classmethod
    def create_store(cls, **kw):
        return create_store('mongodb://127.0.0.1:28017', **kw)

    def test_store(self):
        client = self.store.client()
        alive = client.alive()
        self.assertTrue(alive)
