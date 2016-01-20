define(['angular',
        'lux/services',
        'tests/mocks/http'], function (angular) {
    'use strict';

    describe('Test lux.restapi module', function () {
        var context = {
                API_URL: '/api'
            },
            $lux,
            scope,
            $httpBackend;

        angular.module('lux.restapi.test', ['lux.loader', 'lux.restapi', 'lux.mocks.http'])
            .value('context', context);

        beforeEach(function () {
            module('lux.restapi.test');
            // module('lux.restapi.mock');

            inject(['$lux', '$rootScope', '$httpBackend', function (_$lux_, _$rootScope_, _$httpBackend_) {
                $lux = _$lux_;
                scope = _$rootScope_;
                $httpBackend = _$httpBackend_;
            }]);

        });

        it('Luxrest api object', function () {
            expect(angular.isFunction(scope.api)).toBe(true);
            var client = scope.api();
            expect(angular.isObject(client)).toBe(true);

            expect(client.baseUrl()).toBe('/api');
        });

        it('populates the API URLs', function () {
            var client = scope.api();
            $httpBackend.expectGET(context.API_URL).respond(mock_data);
            client.populateApiUrls();
            $httpBackend.flush();
            expect($lux.apiUrls[context.API_URL]['authorizations_url']).toBe('/api/authorizations');
        });

        it('gets API URLs', function () {
            var client = scope.api(),
                apiNames = {};
            $httpBackend.expectGET(context.API_URL).respond(mock_data);
            client.getApiNames().then(function (_apiNames_) {
                apiNames = _apiNames_;
            });
            $httpBackend.flush();
            expect(apiNames['authorizations_url']).toBe('/api/authorizations');
        });

        it('gets a URL for an API target', function () {
            var client = scope.api(),
                url = '';
            $httpBackend.expectGET(context.API_URL).respond(mock_data);
            client.getUrlForTarget({
                url: context.API_URL,
                name: 'authorizations_url',
                path: 'test'
            }).then(function (_url_) {
                url = _url_;
            });
            $httpBackend.flush();
            expect(url).toBe('/api/authorizations/test');
        });
    });

});
