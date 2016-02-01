import json

from pulsar.apps import rpc
from pulsar.apps.data import PubSubClient
from pulsar.utils.string import to_string


class PubSub:
    """Implement the publish and subscribe websocket RPC calls
    """
    def ws_publish(self, wsrequest):
        """Publish an event on a channel

        From the client::

            client.rpc('publish', {'channel': 'mychannel',
                                   'event': 'myevent',
                                   'data': data})
        """
        channels, channel, event = Channels.get(wsrequest)
        msg = get_publish_message(wsrequest, event)
        pubsub = channels.pubsub()
        return pubsub.publish(channel, msg)

    def ws_subscribe(self, wsrequest):
        """Subscribe to an event on a channel

        From the client::

            client.rpc('subscribe', {'channel': 'mychannel',
                                     'event': 'myevent'})
        """
        channels, channel, event = Channels.get(wsrequest)
        return channels.register(channel, event)


class Channels(PubSubClient):
    __slots__ = ('ws', 'channels')

    def __init__(self, ws):
        self.ws = ws
        self.channels = {}
        pubsub = self.pubsub()
        pubsub.add_client(self)

    def __repr__(self):
        return repr(self.channels)
    __str__ = __repr__

    @classmethod
    def get(cls, wsrequest):
        params = wsrequest.params
        channel = params.get('channel')
        if not channel:
            raise rpc.InvalidParams('missing channel')
        event = params.get('event')
        if not event:
            raise rpc.InvalidParams('missing event')
        cache = wsrequest.cache
        channels = cache.ws_pubsub_channels
        if channels is None:
            channels = cls(wsrequest.ws)
            cache.ws_pubsub_channels = channels
        return channels, channel, event

    def __call__(self, channel, message):
        events = self.channels.get(channel)
        if events:
            message = json.loads(message.decode('utf-8'))
            event = message.pop('event', None)
            if event and event in events:
                self.ws.write_message(event, channel, message)

    def pubsub(self):
        return self.ws.pubsub()

    def register(self, channel, event):
        """Register a channel event

        :param ws: websocket
        :param name: channel name
        :param event: event name
        :return: a Channel
        """
        events = self.channels.get(channel)
        if events is None:
            events = set()
            self.channels[channel] = events
        events.add(event)
        pubsub = self.pubsub()
        pubsub.subscribe(channel)
        channels = pubsub.channels()
        return [to_string(c) for c in channels]


def get_publish_message(wsrequest, event):
    data = wsrequest.params.get('data')
    user = wsrequest.cache.user_info
    msg = {'event': event}
    if data:
        data['data'] = data
    if user:
        msg['user'] = user
    return msg