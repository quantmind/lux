import json
import re
from collections import namedtuple

from pulsar import ProtocolError
from pulsar.utils.string import to_string
from pulsar.utils.slugify import slugify
from pulsar.apps.data import create_store, PubSubClient
from pulsar.apps.ds import redis_to_py_pattern
from pulsar.utils.importer import module_attribute

from .component import AppComponent, AppProxy


regex_callbacks = namedtuple('regex_callbacks', 'regex callbacks')


class Channels(AppComponent, PubSubClient):
    """Manage channels for publish/subscribe
    """
    def __init__(self, app):
        super().__init__(app)
        self.channels = {}
        self.protocol = module_attribute(app.config['PUBSUB_PROTOCOL'])()
        self._pubsub = None
        prefix = self.app.config['PUBSUB_PREFIX']
        if prefix is None:
            prefix = '%s-' % slugify(self.app.config['APP_NAME'])
        self._prefix = prefix.lower()

    def __repr__(self):
        return repr(self.channels)

    def __len__(self):
        return len(self.channels)

    def __contains__(self, name):
        return name in self.channels

    def register(self, channel_name, event, callback):
        """Register a callback to channel ``event``

        A prefix will be added to the channel name if not already available or
        the prefix is an empty string

        :param channel_name: channel name
        :param event: event name
        :param callback: callback to execute when event on channel occurs
        :return: the list of channels subscribed
        """
        pubsub = self._get()
        if not pubsub:
            return
        channel_name = self._channel_name(channel_name)
        channel = self.channels.get(channel_name)
        subscribe = False
        if channel is None:
            channel = Channel(self, channel_name)
            self.channels[channel.name] = channel
            subscribe = True
        channel.register(event, callback)
        if subscribe:
            pubsub.subscribe(channel.name)
            pubsub.add_client(self)
            channels = pubsub.channels()
            return [to_string(c) for c in channels]

    def publish(self, channel, event, data=None, user=None):
        """Publish a new ``event` on a ``channel``

        :param channel: channel name
        :param event: event name
        :param data: optional payload to include in the event
        :param user: optional user to include in the event
        """
        pubsub = self._get()
        if not pubsub:
            return
        msg = self.get_publish_message(event, data=data, user=user)
        channel = self._channel_name(channel)
        return pubsub.publish(channel, msg)

    # INTERNALS
    def green_middleware(self, environ, start_response):
        """Add a middleeware when running with greenlets.

        This middleware register the app.reload callback to
        the server.reload event
        """
        app = self.app
        self.register('server', 'reload', app.reload)

    def get_publish_message(self, event, data=None, user=None):
        msg = {'event': event}
        msg['data'] = data if data is not None else {}
        if user:
            msg['data']['user'] = user
        return msg

    def __call__(self, channel_name, message):
        channel = self.channels.get(channel_name)
        if channel:
            channel(message)
        else:
            self.app.logger.warning(
                'Got message on channel "%s" with no handlers', channel_name)

    def _channel_name(self, channel):
        if not self._prefix or channel.startswith(self._prefix):
            return channel
        else:
            return ('%s%s' % (self._prefix, channel)).lower()

    def _get(self):
        """Get a pub-sub handler for a given key

        A key is used to group together pub-subs so that bandwidths is reduced
        If no key is provided the handler is not included in the pubsub cache.
        """
        app = self.app
        if self._pubsub is None:
            addr = app.config['PUBSUB_STORE']
            if addr:
                store = create_store(addr)
            else:
                return
            self._pubsub = store.pubsub(protocol=self.protocol)

        pubsub = self._pubsub

        if pubsub and app.green_pool:
            pubsub = GreenPubSub(app.green_pool, pubsub)

        return pubsub


class Channel(AppProxy):
    """Lux Channel

    .. attribute:: channels

        the channels container

    .. attribute:: name

        channel name

    .. attribute:: callbacks

        dictionary mapping events to callbacks
    """
    def __init__(self, channels, name):
        self.channels = channels
        self.name = name
        self.callbacks = {}

    @property
    def app(self):
        """:class:`.Application` this channel belong to
        """
        return self.channels.app

    def __repr__(self):
        return repr(self.callbacks)

    def __call__(self, message):
        event = message.pop('event', '')
        data = message.get('data')
        for regex, callbacks in self.callbacks.values():
            match = regex.match(event)
            if match:
                match = match.group()
                for callback in callbacks:
                    callback(self, match, data)

    def register(self, event, callback):
        """Register a ``callback`` for ``event``
        """
        regex = redis_to_py_pattern(event)
        entry = self.callbacks.get(regex)
        if not entry:
            entry = regex_callbacks(re.compile(regex), [])
            self.callbacks[regex] = entry

        if callback not in entry.callbacks:
            entry.callbacks.append(callback)

        return entry


class Json:

    def encode(self, msg):
        return json.dumps(msg)

    def decode(self, msg):
        try:
            return json.loads(to_string(msg))
        except Exception as exc:
            raise ProtocolError('Invalid JSON') from exc


class GreenPubSub:
    __slots__ = ('pool', '_pubsub')

    def __init__(self, pool, pubsub):
        self.pool = pool
        self._pubsub = pubsub

    def __repr__(self):
        return repr(self._pubsub)
    __str__ = __repr__

    @property
    def _protocol(self):
        return self._pubsub._protocol

    def publish(self, channel, message):
        return self.pool.wait(self._pubsub.publish(channel, message))

    def subscribe(self, channel, *channels):
        return self.pool.wait(self._pubsub.subscribe(channel, *channels))

    def channels(self, pattern=None):
        return self.pool.wait(self._pubsub.channels(pattern=pattern))

    def add_client(self, client):
        self._pubsub.add_client(client)
