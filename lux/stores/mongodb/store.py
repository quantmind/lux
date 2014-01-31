from functools import partial

from pulsar import Pool, coroutine_return
from pulsar.apps.data import Store, register_store
from pulsar.apps.green import green_run, GreenProtocol

import pymongo
from pymongo.pool import SocketInfo

from .client import MongoDbClient


class MongoDbConnection(GreenProtocol):
    pass


class MongoDbPool(object):
    '''A connection pool for pymongo client
    '''
    def __init__(self, store, pair, max_size, net_timeout, conn_timeout,
                 use_ssl, use_greenlets, ssl_keyfile=None, ssl_certfile=None,
                 ssl_cert_reqs=None, ssl_ca_certs=None,
                 wait_queue_timeout=None, wait_queue_multiple=None):
        self.pool = None
        self.store = store
        self.max_size = max_size
        self.pool_id = 0
        self.pair = pair

    @property
    def _loop(self):
        return self.store._loop

    def _create_connection(self, pair=None):
        '''Default method for connecting to remote datastore.
        '''
        protocol_factory = self.store.create_protocol
        host, port = pair or self.store._host
        _, protocol = yield self._loop.create_connection(
            protocol_factory, host, port)
        socket_info = SocketInfo(protocol, self.pool_id)
        coroutine_return(socket_info)

    def reset(self):
        if self.pool is not None:
            self.pool.close()
            self.pool = None

    @green_run
    def get_socket(self, pair=None, force=False):
        if self.pool is None:
            self.pool = Pool(self._create_connection, pool_size=self.max_size,
                             loop=self.store._loop)
            self.pool_id += 1
        if force:
            return self._create_connection(pair)
        else:
            return self.pool.connect()

    def maybe_return_socket(self, sock_info):
        pass


class MongoDbStore(Store):
    protocol_factory = MongoDbConnection

    def _init(self, **kw):
        if isinstance(self._host, tuple):
            host, port = self._host
        else:
            raise NotImplementedError('Could not connect to %s' %
                                      str(self._host))
        kw['_pool_class'] = partial(MongoDbPool, self)
        kw['_connect'] = False
        self.delegate = pymongo.MongoClient(host, port, **kw)

    def client(self):
        return MongoDbClient(self)


register_store('mongodb',
               'lux.stores.mongodb.store.MongoDbStore')
