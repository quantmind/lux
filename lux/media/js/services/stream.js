define(['angular',
        'lux/main',
        'lux/stream/main'], function (angular, lux, luxStream) {
    'use strict';
    //
    //  lux.sockjs module
    //  ==================
    //
    //  It adds the ``sockJs`` method to $lux handler.
    //  The method return a new socket Js instance which connect to a
    //  given url.
    //
    angular.module('lux.stream', ['lux.services'])
        .value('luxStreamAppId', lux.context.LUX_STREAM_APPID || 'test')

        .value('luxStreamUrl', null)

        .run(['$lux', 'luxStreamAppId', 'luxStreamUrl', function ($lux, luxStreamAppId, luxStreamUrl) {
            luxStream.log = $lux.log;

            $lux.stream = function (url) {
                return luxStream({
                    appId: luxStreamAppId,
                    url: url || luxStreamUrl,
                    authToken: $lux.user_token
                });
            };

        }]);

    return luxStream;
});
