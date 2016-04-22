from .auth import check_ws_permission


class Channels:
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
        event = wsrequest.required_param('event')
        channels = wsrequest.ws.channels
        data = wsrequest.params.get('data')
        user = wsrequest.cache.user_info
        return channels.publish(channel, event, data, user=user)

    def ws_subscribe(self, wsrequest):
        """Subscribe to an event on a channel

        From the client::

            client.rpc('subscribe', {'channel': 'mychannel',
                                     'event': 'myevent'})
        """
        channel = wsrequest.required_param('channel')
        event = wsrequest.required_param('event')
        check_ws_permission(wsrequest, channel, 'read')
        ws = wsrequest.ws
        channels = ws.channels
        return channels.register(channel, event, ws.write_message)
