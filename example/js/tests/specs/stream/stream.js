define(['angular',
        'lux/services/stream',
        'tests/data/restapi',
        'tests/mocks/http'], function (angular, luxStream) {
    'use strict';

    describe('Test stream module', function () {

        var $lux;

        angular.module('lux.stream.test', ['lux.stream', 'lux.mocks.http'])
            .value('luxStreamAppId', 'jasmine');

        beforeEach(function () {
            module('lux.stream.test');

            inject(function (_$lux_) {
                $lux = _$lux_;
            });
        });

        it('Test luxStream function', function () {
            expect(angular.isFunction(luxStream)).toBe(true);
            expect(angular.isFunction($lux.stream)).toBe(true);
        });

    });
});
