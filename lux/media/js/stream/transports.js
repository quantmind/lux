/* eslint-plugin-disable angular */
define([], function () {
    'use strict';

    var states = {
        initialised: 'initialised',
        connecting: 'connecting',
        connected: 'connected',
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
            events = {};

        return {
            connect: connect,
            write: write,
            close: close,
            bind: bind,
            status: function () {
                return status;
            },
            connected: function () {
                return status === states.connected;
            }
        };

        function bind (event, callback) {
            var callbacks = events[event];
            if (!callbacks) {
                callbacks = [];
                events[event] = callbacks;
            }
            callbacks.push(callback);
            return self;
        }

        function fire (event) {
            var callbacks = events[event];
            if (callbacks)
                callbacks.forEach(function (cbk) {
                    cbk(self);
                });
        }

        function reconnect () {
            if (status === states.unavailable) {
                if (self.opened()) {
                    status = states.initialised;
                    connect();
                } else
                    fire_disconnected();
            }
        }

        function connect (onOpen) {
            if (!self.open()) return fire_disconnected();

            if (onOpen)
                pending.push(onOpen);

            if (status === states.initialised) {
                status = states.connecting;
                fire(status);
                require(['sockjs'], function (SockJs) {
                    initialise(SockJs);
                });
            } else if (status === states.connected) {
                var execute = pending;
                pending = [];
                execute.forEach(function (cbk) {
                    cbk(self);
                });
            }
        }

        function write (msg) {
            return connect(function () {
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

        function fire_connected (user) {
            self.user = user;
            status = states.connected;
            fire(status);
            setTimeout(connect, 100);
        }

        function fire_disconnected () {
            status = states.disconnected;
            self.log.warn('Connection with ' + self.getUrl() + ' CLOSED');
            fire(status);
        }

        function initialise (SockJs) {
            var _sock = new SockJs(self.getUrl());

            _sock.onopen = function () {
                sock = _sock;
                self.log.info('New web socket connection with ' + self.getUrl());
                self.reconnectTime.reset();

                if (config.authToken)
                    self.rpc('authenticate', {token: config.authToken}, function (response) {
                        fire_connected(response.result);
                    }, function (response) {
                        self.log.error('Could not authenticate: ' + response.error.message);
                        fire_connected();
                    });
                else
                    fire_connected();
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
    }

});
