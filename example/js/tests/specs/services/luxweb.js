define(['angular',
        'lux/services',
        'tests/data/restapi',
        'tests/mocks/http'], function (angular) {
    'use strict';

    describe('Test lux.webapi module', function () {

        var $lux;

        angular.module('lux.webapi.test', ['lux.loader', 'lux.mocks.http', 'lux.webapi'])
            .value('context', {API_URL: '/api'});

        beforeEach(function () {
            module('lux.webapi.test');

            inject(function (_$lux_) {
                $lux = _$lux_;
            });
        });

    });

});
