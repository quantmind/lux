/* eslint-plugin-disable angular */
define([], function () {
    'use strict';

    var states = {
        initialised: 'initialised',
        connecting: 'connecting',
        connected: 'connected',
        ready: 'ready',
        unavailable: 'unavailable',
        disconnected: 'disconnected'
    };

    return {
        sockjs: sockjs
    };

    function sockjs (self, config) {
        var sock = null,
            status = states.initialised,
            pending = [],
            // Channel for connection events
            channel = self.subscribe('connection');

        channel.bind('connection_established', authenticate);
        channel.bind('ready', execute);

        return {
            connect: execute,
            write: write,
            close: close,
            bind: channel.bind,
            unbind: channel.unbind,
            status: function () {
                return status;
            },
            connected: function () {
                return status === states.connected;
            }
        };

        function can_execute () {
            return status === states.connected || status === states.ready;
        }

        function can_connect () {
            return status === states.initialised || status === states.unavailable;
        }

        function reconnect () {
            if (status === states.unavailable) {
                if (self.opened()) {
                    execute();
                } else
                    fire_disconnected();
            }
        }

        function execute () {
            if (!self.opened()) return fire_disconnected();

            if (can_connect()) {
                status = states.connecting;
                channel.fire(status);
                require(['sockjs'], function (SockJs) {
                    initialise(SockJs);
                });
            } else if (can_execute()) {
                var toExecute = pending;
                pending = [];
                toExecute.forEach(function (cbk) {
                    cbk.call(self);
                });
            }
        }

        function write (msg) {
            pending.push(function () {
                sock.send(self.encode(msg));
            });
            execute();
        }

        function close () {
            if (sock) {
                status = states.disconnected;
                sock.close();
                sock = null;
            }
        }

        function fire_disconnected () {
            status = states.disconnected;
            self.log.warn('luxStream: connection with ' + self.getUrl() + ' CLOSED');
            channel.fire(status);
        }

        function initialise (SockJs) {
            var _sock = new SockJs(self.getUrl());

            _sock.onopen = function () {
                sock = _sock;
                self.log.debug('luxStream: new connection with ' + self.getUrl());
                self.reconnectTime.reset();
                status = states.connected;
                channel.fire(status);
            };

            _sock.onmessage = function (e) {
                var msg = self.decode(e.data);
                // A message on a channel
                if (msg.channel)
                    self.subscribe.onMessage(msg.channel, msg.event, msg.data);
                else
                // An rpc response
                    self.rpc.onMessage(msg);
            };

            _sock.onclose = function () {
                sock = null;
                if (self.opened()) {
                    status = states.unavailable;
                    var next = self.reconnectTime();
                    self.log.warn('luxStream: lost connection - trying again in ' + 0.001*next + ' seconds.');
                    setTimeout(reconnect, next);
                } else
                    fire_disconnected();
            };
        }

        function authenticate () {
            if (config.authToken) {
                self.rpc('authenticate', {authToken: config.authToken}, function (response) {
                    self.log.debug('luxStream: authentication successful with ' + self.getUrl());
                    fire_ready(response.result);
                }, function (response) {
                    self.log.error('luxStream: could not authenticate: ' + response.error.message);
                    fire_ready();
                });
            } else
                fire_ready();
        }

        function fire_ready (user) {
            self.user = user;
            status = states.ready;
            channel.fire(status);
        }
    }

});
