

class WsChannelsRpc:
    """Mixin for publish/subscribe websocket RPC calls
    """
    def ws_publish(self, wsrequest):
        """Publish an event on a channel

        From the client::

            client.rpc('publish', {'channel': 'mychannel',
                                   'event': 'myevent',
                                   'data': data})
        """
        channel = wsrequest.required_param('channel')
        wsrequest.check_permission(channel, 'update')
        event = wsrequest.required_param('event')
        data = wsrequest.params.get('data')
        return self.channel_publish(wsrequest, channel, event, data)

    def ws_subscribe(self, wsrequest):
        """Subscribe to an event on a channel

        From the client::

            client.rpc('subscribe', {'channel': 'mychannel',
                                     'event': 'myevent'})
        """
        channel = wsrequest.required_param('channel')
        wsrequest.check_permission(channel, 'read')
        event = wsrequest.required_param('event')
        return self.channel_subscribe(wsrequest, channel, event)

    def channel_subscribe(self, wsrequest, channel, event):
        ws = wsrequest.ws
        channels = ws.channels
        return channels.register(channel, event, ws.write_message)

    def channel_publish(self, wsrequest, channel, event, data):
        channels = wsrequest.ws.channels
        user = wsrequest.cache.user_info
        return channels.publish(channel, event, data, user=user)
