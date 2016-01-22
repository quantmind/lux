define(['angular',
        'lux/services',
        'tests/data/restapi',
        'tests/mocks/http'], function (angular, lux, api_mock_data) {
    'use strict';

    describe('Test lux.restapi module', function () {

        var $lux;

        angular.module('lux.restapi.test', ['lux.loader', 'lux.mocks.http', 'lux.restapi'])
            .value('context', {API_URL: '/api'});

        beforeEach(function () {
            module('lux.restapi.test');

            inject(function (_$lux_) {
                $lux = _$lux_;
            });
        });

        it('Luxrest api object', function () {
            expect(angular.isFunction($lux.api)).toBe(true);
            var client = $lux.api('/api');
            expect(angular.isObject(client)).toBe(true);
            expect(client.baseUrl()).toBe('/api');
        });

        it('gets the API URLs', function () {
            var client = $lux.api('/api');

            client.get().expect(function (data) {
                expect(data).toEqual(api_mock_data['/api']);
            });
        });

        it('Gets a list of users', function () {
            var client = $lux.api({url: '/api', name: 'users_url'});
            client.get().expect(function (data) {
                expect(data).toEqual(api_mock_data['/api/users']);
            });
            client.get({path: 'pippo'}).expect(function (data) {
                expect(data).toEqual(api_mock_data['/api/users/pippo']);
            });
        });

    });

});
