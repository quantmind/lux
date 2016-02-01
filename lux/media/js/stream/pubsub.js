/* eslint-plugin-disable angular */
define([], function () {
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

        function Channel(name) {

            var events = {},
                ch = this;

            this.name = function () {
                return name;
            };

            this.message = message;
            this.bind = bind;
            //this.unbind = unbind;

            //
            //  Bind a channel to a given event
            //
            //  The callback is executed every time the event is triggered on
            //  this channel
            function bind(event, callback) {
                event = '' + event;
                if (event) {
                    var callbacks = events[event];
                    if (!callbacks) {
                        callbacks = [];
                        events[event] = callbacks;
                        var data = {
                            channel: name,
                            event: event
                        };
                        self.transport.bind('connected', function () {
                            self.rpc('subscribe', data);
                        });
                    }
                    callbacks.push(callback);
                    return true;
                }
                return false;
            }

            function message(event, message) {
                var callbacks = events[event];
                if (callbacks)
                    callbacks.forEach(function (cbk) {
                        cbk(event, message, ch);
                    });
            }
        }

        //  Subscribe to a given channel
        //  ----------------------------------------
        //
        //  Return a channel instance
        function subscribe(channel) {
            channel = '' + channel;
            if (channel) {
                var c = channels[channel];
                if (!c) {
                    c = new Channel(channel);
                    channels[channel] = c;
                }
                return c;
            }
        }

        function onMessage(channel, event, data) {
            var c = channels[channel];
            if (c)
                c.message(event, data);
            else
                self.log.error('Got message without channel');
        }

        subscribe.onMessage = onMessage;

        return subscribe;
    }
});
