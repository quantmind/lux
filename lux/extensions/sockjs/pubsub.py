import json

from pulsar.apps import rpc
from pulsar.apps.data import PubSubClient


class Channels(PubSubClient):
    __slots__ = ('ws', 'channels')

    def __init__(self, ws):
        self.ws = ws
        self.channels = {}
        pubsub = self.pubsub()
        pubsub.add_client(self)

    @classmethod
    def get(cls, ws):
        cache = ws.cache
        channels = cache.ws_pubsub_channels
        if channels is None:
            channels = cls(ws)
            cache.ws_pubsub_channels = channels
        return channels

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
            pubsub = self.pubsub()
            yield from pubsub.subscribe(channel)
        channel.add(event)


class PubSub:

    def ws_publish(self, request):
        """Publish a message
        """
        params = request.params
        channel = params.get('channel')
        if not channel:
            raise rpc.InvalidParams('Cannot publish, no channel given')
        event = params.get('event')
        if not event:
            raise rpc.InvalidParams('Cannot publish, no event given '
                                    'for channel "%s"' % channel)
        msg = self.get_publish_message(request, event, params.get('data'))
        channels = Channels.get(request.ws)
        pubsub = channels.pubsub()
        yield from pubsub.publish(channel, msg)
        return True

    def ws_subscribe(self, request):
        """Subscribe to an event on a channel
        """
        params = request.params
        channel = params.get('channel')
        if not channel:
            raise rpc.InvalidParams('Cannot subscribe, no channel given')
        event = params.get('event')
        if not event:
            raise rpc.InvalidParams('Cannot subscribe, no event given '
                                    'for channel "%s"' % channel)
        channels = Channels.get(request.ws)
        return channels.register(channel, event)

    def get_publish_message(self, request, event, data):
        user = request.cache.user_info
        msg = {'event': event, 'data': data}
        if user:
            msg['user'] = user
        return json.dumps(msg)
