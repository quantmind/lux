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
                expect(data).toBe(api_mock_data['/api']);
            });
        });

        //it('gets a URL for an API target',
        //    inject(['$lux', function ($lux) {
        //        var client = $lux.api('/api');
        //        var response = client.get('users');
        //        expect(response).toBe(mock_data['/api/users']);
                //$httpBackend.expectGET(context.API_URL).respond(mock_data);
                //client.getUrlForTarget({
                //    url: context.API_URL,
                //    name: 'authorizations_url',
                //   path: 'test'
                //}).then(function (_url_) {
                //    url = _url_;
                //});
                //$httpBackend.flush();
                //expect(url).toBe('/api/authorizations/test');
        //    }])
        //);

    });

});
