/* eslint-plugin-disable angular */
define(['lux/config/main',
        'lux/stream/transports',
        'lux/stream/backoffs',
        'lux/stream/rpc',
        'lux/stream/pubsub'], function (lux, transports, backOffs, rpcProtocol, pubsub) {
    'use strict';

    var version = '1.0',
        streamApps = {};

    var defaults = {
        url: null,
        transport: 'sockjs',
        parser: 'json',
        backOff: 'exponential',
        minReconnectTime: 500,
        maxReconnectTime: 5000
    };

    var parsers = {};

    parsers.json = function () {

        return  {
            encode: function (msg) {
                return JSON.stringify(msg);
            },
            decode: function (msg) {
                return JSON.parse(msg);
            }
        };
    };

    function LuxStreamException(message) {
        this.message = message;
        this.name = 'LuxStreamException';
    }
    //
    //  Websocket for RPC and pub/sub messages
    //  =========================================
    //
    //  An instance of ``sockJs`` can be obtained via the ``$lux.sockJs``
    //  method:
    //
    //      sock = $lux.sockJs(url);
    //
    //  Usage:
    //
    //  var stream = new LuxStream({appId: <appId>, token: <token>});
    //
    function luxStream (config) {
        config = lux.extend({}, luxStream.defaults, config);
        if (!config.appId)
            throw new LuxStreamException('luxStream: appId is required');

        var self = streamApps[config.appId];

        if (!self) {
            if (!config.url)
                throw new LuxStreamException('luxStream: url is required');
            self = new luxStream.LuxStream(config);
            streamApps[self.id()] = self;
        }

        return self;
    }

    function LuxStream (config) {
        var self = this,
            open = true;

        lux.extend(self, luxStream.parsers[config.parser](self), {
            Exception: LuxStreamException,
            config: config,
            id: function () {
                return config.appId;
            },
            getUrl: function () {
                return config.url;
            },
            version: function () {
                return version;
            },
            log: luxStream.log,
            rpc: luxStream.rpcProtocol(self),
            publish: luxStream.pubsub.publish(self),
            subscribe: luxStream.pubsub.subscribe(self),
            reconnectTime: luxStream.backOffs[config.backOff](self, config),
            opened: function () {
                return open;
            },
            close: function () {
                if (open) {
                    open = false;
                    self.transport.close();
                }
                return self;
            }
        });

        self.transport = luxStream.transports[config.transport](self, config);
        self.transport.connect();
    }

    luxStream.LuxStream = LuxStream;
    luxStream.rpcProtocol = rpcProtocol;
    luxStream.pubsub = pubsub;
    luxStream.defaults = defaults;
    luxStream.transports = transports;
    luxStream.parsers = parsers;
    luxStream.backOffs = backOffs;
    luxStream.log = {};

    return luxStream;
});
