    //
    //  SockJS Module
    //  ==================
    //
    //
    //
    angular.module('lux.sockjs', [])

        .run(['$rootScope', '$log', function (scope, log) {

            var websockets = {},
                websocketChannels = {};

            scope.addWebsocketListener = function (channel, listener) {
                var listeners = websocketChannels[channel];
                if (!listeners) {
                    listeners = [];
                    websocketChannels[channel] = listeners;
                }
                listeners.push(listener);
            };

            scope.sendMessage = function (url, msg, forceEncode) {
                var sock = websockets[url];
                if (!sock) {
                    log.error('Attempted to send message to disconnected WebSocket: ' + url);
                } else {
                    if (typeof msg !== 'string' || forceEncode) {
                        msg = JSON.stringify(msg);
                    }
                    sock.send(msg);
                }
            };

            scope.disconnectSockJs = function(url) {
                if (websockets[url])
                    websockets[url].close();
            };

            scope.connectSockJs = function (url) {
                if (websockets[url]) {
                    log.warn('Already connected with ' + url);
                    return;
                }

                require(['sockjs'], function (SockJs) {
                    var sock = new SockJs(url);

                    websockets[url] = sock;

                    sock.onopen = function() {
                        websockets[url] = sock;
                        log.info('New connection with ' + url);

                        angular.forEach(Object.keys(websocketChannels), function(channel) {
                            angular.forEach(websocketChannels[channel], function(listener) {
                                listener.onConnect();
                            });
                        });
                    };

                    sock.onmessage = function (e) {
                        var msg = angular.fromJson(e.data),
                            listeners;
                        log.info('event', msg.event);
                        if (msg.channel)
                            listeners = websocketChannels[msg.channel];
                        if (msg.data)
                            msg.data = angular.fromJson(msg.data);
                        angular.forEach(listeners, function (listener) {
                            listener.onMessage(sock, msg);
                        });

                    };

                    sock.onclose = function() {
                        delete websockets[url];
                        log.warn('Connection with ' + url + ' CLOSED');
                    };
                });
            };

            if (scope.STREAM_URL)
                scope.connectSockJs(scope.STREAM_URL);
        }]);
