define(['angular',
        'lux'], function (angular) {
    'use strict';

    //
    // Websocket handler for RPC and pub/sub messages
    function sockJs($lux, url, websockets, websocketChannels) {
        var handler = {},
            log = $lux.log,
            context = websockets[url];

        if (!context) {
            context = {
                executed: {},
                id: 0
            };

            websockets[url] = context;
        }

        handler.getUrl = function () {
            return url;
        };

        // RPC call
        //
        //  method: rpc method to call
        //  data: optional object with rpc parameters
        //  callback: optional callback invoked when a response is received
        handler.rpc = function (method, data, callback) {
            data = {
                method: method,
                id: ++context.id,
                data: data
            };
            var msg = angular.toJson(data);
            if (callback) {
                context.executed[data.id] = callback;
            }
            return handler.sendMessage(msg);
        };

        handler.connect = function (onopen) {
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
                                    if (msg.data.rpcComplete) {
                                        delete context.executed[msg.data.id];
                                    }
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
            return handler;
        };

        handler.sendMessage = function (msg, forceEncode) {
            return handler.connect(function (sock) {
                if (!angular.isString(msg) || forceEncode) {
                    msg = angular.fromJson(msg);
                }
                sock.send(msg);
            });
        };

        handler.disconnect = function () {
            var sock = context.sock;

            if (angular.isArray(sock))
                sock.push(function (s) {
                    s.close();
                });
            else if (sock)
                sock.close();
            return handler;
        };

        handler.addListener = function (channel, callback) {
            var callbacks = websocketChannels[channel];
            if (!callbacks) {
                callbacks = [];
                websocketChannels[channel] = callbacks;
            }
            callbacks.push(callback);
        };

        return handler;
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
