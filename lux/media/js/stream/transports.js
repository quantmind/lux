/* eslint-plugin-disable angular */
define([], function () {
    'use strict';

    var states = {
        initialised: 0,
        connecting: 1,
        connected: 2,
        ready: 3,
        unavailable: 4,
        disconnected: 5
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

        function reconnect () {
            if (status === states.unavailable) {
                if (self.opened()) {
                    status = states.initialised;
                    execute();
                } else
                    fire_disconnected();
            }
        }

        function execute (onOpen) {
            if (!self.opened()) return fire_disconnected();

            if (onOpen)
                pending.push(onOpen);

            if (status === states.initialised) {
                status = states.connecting;
                channel.fire(status);
                require(['sockjs'], function (SockJs) {
                    initialise(SockJs);
                });
            } else if (can_execute()) {
                var execute = pending;
                pending = [];
                execute.forEach(function (cbk) {
                    cbk(self);
                });
            }
        }

        function write (msg) {
            return execute(function () {
                sock.send(self.encode(msg));
            });
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
            self.log.warn('Connection with ' + self.getUrl() + ' CLOSED');
            channel.fire(status);
        }

        function initialise (SockJs) {
            var _sock = new SockJs(self.getUrl());

            _sock.onopen = function () {
                sock = _sock;
                self.log.info('New web socket connection with ' + self.getUrl());
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
                    self.log.warn('Lost connection. Trying again in ' + 0.001*next + ' seconds.');
                    setTimeout(reconnect, next);
                } else
                    fire_disconnected();
            };
        }

        function authenticate () {
            if (config.authToken) {
                self.rpc('authenticate', {authToken: config.authToken}, function (response) {
                    fire_ready(response.result);
                }, function (response) {
                    self.log.error('Could not authenticate: ' + response.error.message);
                    fire_ready();
                });
            }
            fire_ready();
        }

        function fire_ready (user) {
            self.user = user;
            status = states.ready;
            channel.fire(status);
        }
    }

});
