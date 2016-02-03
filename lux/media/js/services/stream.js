define(['angular',
        'lux',
        'lux/stream'], function (angular, lux, luxStream) {
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

        .run(['$lux', 'luxStreamAppId', function ($lux, luxStreamAppId) {
            luxStream.log = $lux.log;

            $lux.stream = function (url) {
                return luxStream({
                    appId: luxStreamAppId,
                    url: url,
                    authToken: $lux.user_token
                });
            };

        }]);

    return luxStream;
});
