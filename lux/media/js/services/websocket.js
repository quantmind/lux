define(['angular',
        'lux/stream',
        'lux'], function (angular, luxStream) {
    'use strict';
    //
    //  lux.sockjs module
    //  ==================
    //
    //  It adds the ``sockJs`` method to $lux handler.
    //  The method return a new socket Js instance which connect to a
    //  given url.
    //
    angular.module('lux.sockjs', ['lux.services'])

        .run(['$lux', function ($lux) {
            luxStream.log = $lux.messages;

            $lux.stream = luxStream;

        }]);

});
