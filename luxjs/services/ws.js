 //
 // Websocket handler for RPC and pub/sub messages
function sockJs (url, websockets, websocketChannels, log) {
    var handler = {},
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
        var msg = JSON.stringify(data);
        data.callback = callback;
        context.executed[data.id] = data;
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
                    angular.forEach(listeners, function (listener) {
                        listener(sock, msg);
                    });

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
            if (typeof msg !== 'string' || forceEncode) {
                msg = JSON.stringify(msg);
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
//  Sock module
//  ==================
//
//
//
angular.module('lux.sockjs', [])

    .run(['$rootScope', '$log', function (scope, log) {

        var websockets = {},
            websocketChannels = {};

        scope.sockJs = function (url) {
            return sockJs(url, websockets, websocketChannels, log);
        };

    }]);
