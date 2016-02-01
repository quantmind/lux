/* eslint-plugin-disable angular */
define([], function () {
    'use strict';

    return rpcProtocol;


    function rpcProtocol (self) {

        var protocol = 'rpc',
            executed = {},
            idCounter = 0,
            empty = {};

        //  RPC call
        //  ---------------
        //
        //  Low level method for all rpc calls
        //
        //  method: rpc method to call
        //  data: optional object with rpc parameters
        //  callback: optional callback invoked when a response is received
        function rpc(method, data, callBack, errorBack) {
            var msg = {
                protocol: protocol,
                method: method,
                appId: self.id(),
                id: newId(),
                version: self.version(),
                data: data
            };
            if (callBack || errorBack) {
                executed[msg.id] = {
                    success: callBack,
                    error: errorBack || callBack
                };
            }
            return self.transport.write(msg);
        }

        //
        // Handle an RPC message from server (a response)
        function onMessage(response) {
            if (response.id) {
                var callback = executed[response.id] || empty;
                // Check if an rpc response is a good one, otherwise log the error
                if (response.error) {
                    self.log.error(response.error.message);
                    if (callback.error) callback.error(response);
                } else if (callback.success) {
                    callback.success(response);
                }
                if (response.complete)
                    delete executed[response.id];
            } else
                self.log.error('Received an RPC message without id');
        }

        //  authenticate
        //  -----------------
        //
        //  Authenticate with backend
        //
        //  If authentication is successful, the self instance will
        //  contain the ``user`` attribute
        function authenticate (token, callBack, errorBack) {
            self.rpc('authenticate', {token: token}, function (response) {
                self.user = response.result;
                if (callBack)
                    callBack.call(arguments);
            }, errorBack || callBack);
        }

        rpc.onMessage = onMessage;
        rpc.authenticate = authenticate;
        rpc.protocol = protocol;

        return rpc;

        function newId() {
            var id = ++idCounter;
            return protocol + id;
        }
    }

});
