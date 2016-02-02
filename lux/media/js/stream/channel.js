define([], function () {
    'use strict';

    return Channel;

    function Channel(self, channelName) {

        var events = {},
            channel = this,
            transport = channelName === 'connection';

        this.name = function () {
            return name;
        };

        this.message = message;
        this.bind = bind;
        this.unbind = unbind;
        this.fire = fire;

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
                    if (!transport) {
                        var data = {
                            channel: channelName,
                            event: event
                        };
                        self.transport.bind('ready', function () {
                            self.rpc('subscribe', data);
                        });
                    }
                }
                callbacks.push(callback);
                return true;
            }
            return false;
        }

        function unbind (event, callback) {
            var callbacks = events[event];
            if (callbacks) {
                var index = callbacks.indexOf(callback);
                if (index >= 0) {
                    var result = callbacks.splice(index, 1)[0];
                    if (callbacks.length === 0)
                        delete events[event];
                    return result;
                }
            }
        }

        function fire (event) {
            var callbacks = events[event];
            if (callbacks)
                callbacks.forEach(function (cbk) {
                    cbk(channel);
                });
        }

        function message(event, message) {
            var callbacks = events[event];
            if (callbacks)
                callbacks.forEach(function (cbk) {
                    cbk(event, message, channel);
                });
        }
    }
});