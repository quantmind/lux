import json

from pulsar import ProtocolError
from pulsar.utils.string import to_string
from pulsar.apps.data import create_store, PubSubClient
from pulsar.utils.importer import module_attribute


class Channels(PubSubClient):
    """Manage channels for publish/subscribe
    """
    def __init__(self, app):
        self.app = app
        self.channels = {}
        self.protocol = module_attribute(app.config['PUBSUB_PROTOCOL'])()
        self._pubsub = None
        prefix = self.app.config['PUBSUB_PREFIX']
        if prefix is None:
            prefix = '%s-' % self.app.config['APP_NAME']
        self._prefix = prefix.lower()

    def __repr__(self):
        return repr(self.channels)

    def __len__(self):
        return len(self.channels)

    def __contains__(self, name):
        return name in self.channels

    def register(self, channel, event, callback):
        """Register a callback to channel event

        A prefix will be added to the channel name if not already available or
        the prefix is an empty string

        :param channel: channel name
        :param event: event name
        :param callback: callback to execute when event on channel occurs
        :return: the list of channels subscribed
        """
        pubsub = self._get()
        if not pubsub:
            return
        channel = self._channel_name(channel)
        events = self.channels.get(channel)
        if events is None:
            events = Events()
            self.channels[channel] = events
        events.add(event, callback)
        pubsub.subscribe(channel)
        pubsub.add_client(self)
        channels = pubsub.channels()
        return [to_string(c) for c in channels]

    def publish(self, channel, event, data=None, user=None):
        pubsub = self._get()
        if not pubsub:
            return
        msg = self.get_publish_message(event, data=data, user=user)
        channel = self._channel_name(channel)
        return pubsub.publish(channel, msg)

    # INTERNALS
    def green_middleware(self, environ, start_response):
        app = self.app
        self.register('server', 'reload', app.reload)

    def get_publish_message(self, event, data=None, user=None):
        msg = {'event': event}
        msg['data'] = data if data is not None else {}
        if user:
            msg['data']['user'] = user
        return msg

    def __call__(self, channel, message):
        events = self.channels.get(channel)
        if events:
            event = message.pop('event', None)
            if event and event in events:
                data = message.get('data')
                for callback in events[event]:
                    callback(channel, event, data)
                return
        self.app.logger.warning(
                'Got message on %s.%s with no handler', channel, event)

    def _channel_name(self, channel):
        if not self._prefix or channel.startswith(self._prefix):
            return channel
        else:
            return ('%s%s' % (self._prefix, channel)).lower()

    def _prefix(self):
        prefix = self.app.config['PUBSUB_PREFIX']
        if prefix is None:
            prefix = '%s-' % self.app.config['APP_NAME']
        return prefix

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


class Events(dict):

    def add(self, event, callback):
        callbacks = self.get(event)
        if not callbacks:
            callbacks = []
            self[event] = callbacks

        if callback not in callbacks:
            callbacks.append(callback)

        return callbacks


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
