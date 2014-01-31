from sqlalchemy import create_engine

import psycopg2
from psycopg2 import ProgrammingError, OperationalError
from psycopg2 import extensions

try:
    extensions.POLL_OK
except AttributeError:
    raise ImproperlyConfigured(
        'Psycopg2 does not have support for asynchronous connections. '
        'You need at least version 2.2.0 of Psycopg2.')

from pulsar.apps.data import Store, register_store


def wait_read(fileno, timeout=None):
    loop = get_event_loop()
    
    
def pulsar_wait_callback(conn, timeout=None):
    """A wait callback useful to allow gevent to work with Psycopg."""
    while 1:
        state = conn.poll()
        if state == extensions.POLL_OK:
            break
        elif state == extensions.POLL_READ:
            wait_read(conn.fileno(), timeout=timeout)
        elif state == extensions.POLL_WRITE:
            wait_write(conn.fileno(), timeout=timeout)
        else:
            raise psycopg2.OperationalError(
                "Bad result from poll: %r" % state)

extensions.set_wait_callback(pulsar_wait_callback)


class Async(object):

    def wait(self, callback, errback=None, registered=False):
        exc = None
        loop = self._loop
        try:
            state = self.connection.poll()
        except Exception:
            exc = sys.exc_info()
            if registered:
                loop.remove_connector(self._sock_fd)
        else:
            if state == POLL_OK:
                if registered:
                    loop.remove_connector(self._sock_fd)
                callback()
            elif not registered:
                loop.add_connector(self._sock_fd, self.wait, callback,
                                   errback, True)
            return
        self.close()
        exc = Failure(exc)
        if errback:
            errback(exc)


class PostgreSqlStore(Store):

    def _init(self, **kw):
        dns = self._buildurl()
        self._sql = create_engine(dns, creator=self._connect)



register_store('postgresql',
               'pulsar.apps.data.stores.postgresql.store.PostgreSql')
