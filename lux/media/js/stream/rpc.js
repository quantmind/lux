/* eslint-plugin-disable angular */
define([], function () {
    'use strict';

    var errors = {};
    errors[-32700] = 'protocol error';
    errors[-32600] = 'invalid request';
    errors[-32601] = 'no such function';
    errors[-32602] = 'invalid parameters';
    errors[-32603] = 'internal error';

    return rpcProtocol;


    function rpcProtocol (self) {

        var executed = {},
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
                method: method,
                appId: self.id(),
                id: newId(),
                version: self.version(),
                params: data
            };
            if (callBack || errorBack) {
                executed[msg.id] = {
                    success: callBack,
                    error: errorBack || callBack
                };
            }
            self.log.debug('luxStream: execute rpc.' + method);
            return self.transport.write(msg);
        }

        //
        // Handle an RPC message from server (a response)
        function onMessage(response) {
            if (response.id) {
                var callback = executed[response.id] || empty;
                // Check if an rpc response is a good one, otherwise log the error
                if (response.error) {
                    self.log.error('luxStream: rpc ' + errors[response.error.code] +
                        ' (' + response.error.code + ') - ' +
                        response.error.message);
                    if (callback.error) callback.error(response);
                } else if (callback.success) {
                    callback.success(response);
                }
                if (response.complete)
                    delete executed[response.id];
            } else
                self.log.error('luxStream: received an rpc message without id');
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

        return rpc;

        function newId() {
            var id = ++idCounter;
            return 'rpc' + id;
        }
    }

});
