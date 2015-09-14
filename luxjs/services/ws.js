 //
 // Websocket handler for RPC and pub/sub messages
 function sockJs (url, websockets, websocketChannels, log) {
        var hnd = {},
            context = websockets[url];

        if (!context) {
            context = {
                executed: {},
                id: 0
            };

            websockets[url] = context;
        }

        //
        // Return this socket handler url
        hnd.url = function () {
            return url;
        };

        //
        //  RPC call
        //
        //  @param method: rpc method to call
        //  @param data: optional object with rpc parameters
        //  @param callback: optional callback invoked when a response is received
        //  @return the handler
        hnd.rpc = function (method, data, callback) {
            data = {
                method: method,
                id: ++context.id,
                data: data
            };
            var msg = JSON.stringify(data);
            data.callback = callback;
            context.executed[data.id] = data;
            return hnd.sendMessage(msg);
        };

        //
        //  @param callback: optional callback to invoke once the connection
        //      is established or an existing socket is already open
        //  @return the handler
        hnd.connect = function (callback) {
            var sock = context.sock;

            if (angular.isArray(sock)) {
                if (callback) sock.push(callback);
            }
            else if (sock) {
                if (callback) callback(sock);
            } else {
                sock = [];
                context.sock = sock;
                if (callback) sock.push(callback);

                require(['sockjs'], function (SockJs) {
                    var sock = new SockJs(url);

                    sock.onopen = function() {
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
                        angular.forEach(listeners, function (listener) {
                            listener(sock, msg);
                        });

                    };

                    sock.onclose = function() {
                        delete websockets[url];
                        log.warn('Connection with ' + url + ' CLOSED');
                    };
                });
            }
            return hnd;
        };

        hnd.sendMessage = function (msg, forceEncode) {
            return hnd.connect(function (sock) {
                if (typeof msg !== 'string' || forceEncode) {
                    msg = JSON.stringify(msg);
                }
                sock.send(msg);
            });
        };

        hnd.disconnect = function (url) {
            var sock = context.sock;

            if (angular.isArray(sock))
                sock.push(function (s) {
                    s.close();
                });
            else if (sock)
                sock.close();
            return hnd;
        };

        hnd.listener = function (channel, callback) {
            var callbacks = websocketChannels[channel];
            if (!callbacks) {
                callbacks = [];
                websocketChannels[channel] = callbacks;
            }
            callbacks.push(callback);
        };

        return hnd;
    }

    //
    //  Sock module
    //  ==================
    angular.module('lux.sockjs', [])

        .run(['$rootScope', '$log', function (scope, log) {

            var websockets = {},
                websocketChannels = {};

            scope.sockJs = function (url) {
                return sockJs(url, websockets, websocketChannels, log);
            };

        }]);
