define([], function () {
    'use strict';

    return Channel;

    //
    //  Channel
    //  ----------
    //
    //  A channel maintains a given set of events which an application can
    //  bind to (un unbind).
    //
    //  The ``connection`` channel is special, when we bind to an event on
    //  this channel, we don't subscribe to server events, but simply subscribe
    //  to events occurring on the connection
    function Channel(self, channelName) {

        var events = {},
            channel = this,
            transport = channelName === 'connection';

        this.name = function () {
            return name;
        };

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
                self.log.debug('luxStream: binding with ' + channelName + '.' + event);
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
                    self.log.debug('luxStream: unbinding with ' + channelName + '.' + event);
                    var result = callbacks.splice(index, 1)[0];
                    if (callbacks.length === 0)
                        delete events[event];
                    return result;
                }
            }
        }

        function fire (event, message) {
            var callbacks = events[event];
            if (callbacks)
                callbacks.forEach(function (cbk) {
                    cbk.call(channel, event, message);
                });
        }
    }
});
