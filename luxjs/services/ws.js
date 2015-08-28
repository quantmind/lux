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

            scope.websocketListener = function (channel, callback) {
                var callbacks = websocketChannels[channel];
                if (!callbacks) {
                    callbacks = [];
                    websocketChannels[channel] = callbacks;
                }
                callbacks.push(callback);
            };

            scope.sendMessage = function (url, msg, forceEncode) {
                if (typeof msg !== 'string' || forceEncode) {
                    msg = JSON.stringify(msg);
                }
                websockets[url].send(msg);
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
                            listener(sock, msg);
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
