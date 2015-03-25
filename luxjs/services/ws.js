
    angular.module('lux.sockjs', [])

        .run(['$rootScope', '$log', function (scope, log) {
            var websocket = scope.STREAM_URL,
                websocketChannels = {};

            scope.websocketListener = function (channel, callback) {
                var callbacks = websocketChannels[channel];
                if (!callbacks) {
                    callbacks = [];
                    websocketChannels[channel] = callbacks;
                }
                callbacks.push(callback);
            };

            if (websocket) {
                require(['sockjs'], function (SockJs) {
                    var sock = new SockJs(websocket);

                    sock.onopen = function() {
                        log.info('New connection with ' + websocket);
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
                        log.warn('Connection with ' + websocket + ' CLOSED');
                    };
                });
            }
        }]);