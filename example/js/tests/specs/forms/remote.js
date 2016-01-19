define(['angular',
        'lux',
        'tests/data/restapi',
        'tests/mocks/utils',
        'lux/forms'], function (angular, lux, api_mock_data) {
    'use strict';

    describe('Remote options', function () {
        // Define the tree test module
        angular.module('lux.remote.test', []);

        var $compile,
            $rootScope,
            $httpBackend;

        beforeEach(module('lux.remote.test'));

        // Store references to $rootScope and $compile
        // so they are available to all tests in this describe block
        beforeEach(inject(function (_$compile_, _$rootScope_, _$httpBackend_) {
            // The injector unwraps the underscores (_) from around the parameter names when matching
            $compile = _$compile_;
            $rootScope = _$rootScope_;
            $httpBackend = _$httpBackend_;
        }));

        afterEach(function () {
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        });

        it('has two options', function () {
            for (var url in api_mock_data) {
                $httpBackend.when('GET', lux.context.API_URL + url).respond(api_mock_data[url]);
            }
            var element = angular.element('<div data-bmll-remoteoptions data-bmll-remoteoptions-name="exchanges_url"></div>');
            element = $compile(element)($rootScope);
            $rootScope.$digest();
            $httpBackend.flush();

            expect(element.scope().exchanges_url.length).toBe(2);

        });
    });

});
