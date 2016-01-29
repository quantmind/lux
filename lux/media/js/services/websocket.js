define(['angular',
        'lux'], function (angular) {
    'use strict';

    //
    // Websocket handler for RPC and pub/sub messages
    function sockJs($lux, url, websockets, websocketChannels) {
        var self = {},
            log = $lux.log,
            context = websockets[url];

        if (!context) {
            context = {
                executed: {},
                id: 0
            };

            websockets[url] = context;
        }

        self.getUrl = function () {
            return url;
        };

        // Check if a result is a good one, otherwise log the error
        self.ok = function (result) {
            if (message.event === 'error')
                $lux.messages.error(result.data);
            else if (message.event === 'message')
                return true;
            return false;
        };
        // RPC call
        //
        //  method: rpc method to call
        //  data: optional object with rpc parameters
        //  callback: optional callback invoked when a response is received
        self.rpc = function (method, data, callback) {
            data = {
                method: method,
                id: ++context.id,
                data: data
            };
            var msg = angular.toJson(data);
            if (callback)
                context.executed[data.id] = callback;
            return self.sendMessage(msg);
        };

        self.connect = function (onopen) {
            var sock = context.sock;

            if (angular.isArray(sock)) {
                if (onopen) sock.push(onopen);
            }
            else if (sock) {
                if (onopen) onopen(sock);
            } else {
                sock = [];
                context.sock = sock;
                if (onopen) sock.push(onopen);

                require(['sockjs'], function (SockJs) {
                    var sock = new SockJs(url);

                    sock.onopen = function () {
                        var callbacks = context.sock;
                        context.sock = sock;
                        log.info('New web socket connection with ' + url);
                        callbacks.forEach(function (cbk) {
                            cbk(sock);
                        });
                    };

                    sock.onmessage = function (e) {
                        var msg = angular.fromJson(e.data),
                            listeners;
                        if (msg.event)
                            log.info('event', msg.event);
                        if (msg.channel)
                            listeners = websocketChannels[msg.channel];
                        if (msg.data)
                            msg.data = angular.fromJson(msg.data);
                        if (msg.channel === 'rpc') {
                            if (angular.isDefined(msg.data.id)) {
                                if (context.executed[msg.data.id]) {
                                    context.executed[msg.data.id](msg.data.data, sock);
                                    if (msg.data.rpcComplete)
                                        delete context.executed[msg.data.id];
                                }
                            }
                        } else {
                            angular.forEach(listeners, function (listener) {
                                listener(sock, msg);
                            });
                        }

                    };

                    sock.onclose = function () {
                        delete websockets[url];
                        log.warn('Connection with ' + url + ' CLOSED');
                    };
                });
            }
            return self;
        };

        self.sendMessage = function (msg, forceEncode) {
            return self.connect(function (sock) {
                if (!angular.isString(msg) || forceEncode) {
                    msg = angular.fromJson(msg);
                }
                sock.send(msg);
            });
        };

        self.disconnect = function () {
            var sock = context.sock;

            if (angular.isArray(sock))
                sock.push(function (s) {
                    s.close();
                });
            else if (sock)
                sock.close();
            return self;
        };

        self.addListener = function (channel, callback) {
            var callbacks = websocketChannels[channel];
            if (!callbacks) {
                callbacks = [];
                websocketChannels[channel] = callbacks;
            }
            callbacks.push(callback);
        };

        // Authenticate with backend
        //
        // If authentication is successful, the self instance will
        // contain the user attribute
        self.authenticate = function (callback) {
            var token = $lux.user_token;
            if (token)
                self.rpc('authenticate', {token: token}, _authentication_done);
            else
                callback(self);

            function _authentication_done (result) {
                if (self.ok(result))
                    self.user = result.data;
                if (callback)
                    callback(self);
            }
        };

        return self;
    }

    //
    //  lux.sockjs module
    //  ==================
    //
    //
    //
    angular.module('lux.sockjs', ['lux.services'])

        .run(['$lux', function ($lux) {

            var websockets = {},
                websocketChannels = {};

            $lux.sockJs = function (url) {
                return sockJs($lux, url, websockets, websocketChannels);
            };

        }]);

});
