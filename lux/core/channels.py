import json
from collections import namedtuple

from pulsar import ProtocolError
from pulsar.utils.string import to_string
from pulsar.apps.data import create_store
from pulsar.utils.importer import module_attribute

from .component import AppComponent


regex_callbacks = namedtuple('regex_callbacks', 'regex callbacks')


class LuxChannels(AppComponent):
    """Manage channels for publish/subscribe
    """
    @classmethod
    def create(cls, app):
        protocol = module_attribute(app.config['PUBSUB_PROTOCOL'])()
        addr = app.config['PUBSUB_STORE']
        if not addr or not app.green_pool:
            return
        store = create_store(addr)
        channels = store.channels(
            protocol=protocol,
            namespace=app.config['PUBSUB_PREFIX']
        )
        return cls(app, channels)

    def __init__(self, app, channels):
        super().__init__(app)
        self.channels = channels

    def __repr__(self):
        return repr(self.channels)

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.channels)

    def __contains__(self, regex):
        return regex in self.channels

    def __iter__(self):
        return iter(self.channels)

    @property
    def protocol(self):
        return self.channels.pubsub.protocol

    @property
    def namespace(self):
        return self.channels.namespace

    def register(self, channel_name, event, callback):
        return self.app.green_pool.wait(
            self._register_connect(channel_name, event, callback)
        )

    def unregister(self, channel_name, event, callback):
        return self.app.green_pool.wait(
            self.channels.unregister(channel_name, event, callback)
        )

    def publish(self, channel_name, event, data=None):
        return self.app.green_pool.wait(
            self.channels.publish(channel_name, event, data)
        )

    # INTERNALS
    def middleware(self, environ, start_response):
        """Add a middleeware when running with greenlets.

        This middleware register the app.reload callback to
        the server.reload event
        """
        app = self.app
        self.register(app.config['CHANNEL_SERVER'], 'reload', app.reload)

    async def _register_connect(self, channel_name, event, callback):
        await self.channels.register(channel_name, event, callback)
        await self.channels.connect()


class Json:

    def encode(self, msg):
        return json.dumps(msg)

    def decode(self, msg):
        try:
            return json.loads(to_string(msg))
        except Exception as exc:
            raise ProtocolError('Invalid JSON') from exc
