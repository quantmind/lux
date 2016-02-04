/* eslint-plugin-disable angular */
define(['lux/stream/channel'], function (Channel) {
    'use strict';

    return {
        publish: publishMethod,
        subscribe: subscribeMethod
    };

    function publishMethod(self) {

        return publish;

        //  Publish to a given channel and event
        //  ----------------------------------------
        //
        function publish(channel, event, data) {
            channel = '' + channel;
            event = '' + event;
            if (channel && event && self.transport.connected()) {
                data = {
                    channel: channel,
                    event: event,
                    data: data
                };
                self.rpc('publish', data);
                return true;
            }
            return false;
        }
    }

    //
    //  PubSub Protocol
    //  -------------------
    //
    //  Exposes the publish and subscribe methods
    //
    //  stream = luxStream();
    //  stream.pubsub.publish('my-channel', {some: data})
    //  stream.pubsub.subscribe('your-channel', listener)
    function subscribeMethod(self) {

        var channels = {};

        //  Subscribe to a given channel
        //  ----------------------------------------
        //
        //  Return a channel instance
        function subscribe(channel) {
            channel = '' + channel;
            if (channel) {
                var c = channels[channel];
                if (!c) {
                    c = new Channel(self, channel);
                    channels[channel] = c;
                }
                return c;
            }
        }

        function onMessage(channel, event, data) {
            var c = channels[channel];
            if (c)
                c.fire(event, data);
            else
                self.log.error('luxStream: got message without channel');
        }

        subscribe.onMessage = onMessage;

        return subscribe;
    }
});
