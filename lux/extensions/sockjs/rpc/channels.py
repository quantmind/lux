from pulsar.apps.data.channels import Channel, CallbackError


class WsChannelsRpc:
    """Mixin for publish/subscribe websocket RPC calls
    """
    def channel_writer(self, ws):
        if not hasattr(ws, 'channel_writer'):
            ws.channel_writer = Writer(ws)
        return ws.channel_writer

    def ws_publish(self, wsrequest):
        """Publish an event on a channel

        From the client::

            client.rpc('publish', {'channel': 'mychannel',
                                   'event': 'myevent',
                                   'data': data})
        """
        channel = wsrequest.required_param('channel')
        event = wsrequest.required_param('event')
        wsrequest.check_permission('channels', 'update', channel, event)
        data = wsrequest.params.get('data')
        return self.channel_publish(wsrequest, channel, event, data)

    def ws_subscribe(self, wsrequest):
        """Subscribe to an event on a channel

        From the client::

            client.rpc('subscribe', {'channel': 'mychannel',
                                     'event': 'myevent'})
        """
        channel = wsrequest.required_param('channel')
        event = wsrequest.required_param('event')
        wsrequest.check_permission('channels', 'read', channel, event)
        return self.channel_subscribe(wsrequest, channel, event)

    def ws_unsubscribe(self, wsrequest):
        """Un-subscribe from an event on a channel

        From the client::

            client.rpc('unsubscribe', {'channel': 'mychannel',
                                       'event': 'myevent'})
        """
        channel = wsrequest.required_param('channel')
        event = wsrequest.required_param('event')
        wsrequest.check_permission('channels', 'read', channel, event)
        return self.channel_unsubscribe(wsrequest, channel, event)

    def channel_subscribe(self, wsrequest, channel, event):
        ws = wsrequest.ws
        channels = ws.channels
        channels.register(channel, event, self.channel_writer(ws))

    def channel_unsubscribe(self, wsrequest, channel, event):
        ws = wsrequest.ws
        channels = ws.channels
        channels.unregister(channel, event, self.channel_writer(ws))

    def channel_publish(self, wsrequest, channel, event, data):
        channels = wsrequest.ws.channels
        user = wsrequest.cache.user_info
        channels.publish(channel, event, data, user=user)


class Writer:

    def __init__(self, ws):
        self.ws = ws

    def __call__(self, channel, event, data):
        if isinstance(channel, Channel):
            channel = channel.name
        try:
            self.ws.write_message(channel, event, data)
        except RuntimeError:
            raise CallbackError from None
