define(['angular',
        'tests/data/restapi',
        'angular-mocks'], function (angular, api_mock_data) {
    'use strict';

    angular.module('lux.mocks.http', [])

        .config(['$provide', function ($provide) {

            $provide.decorator('$httpBackend', angular.mock.e2e.$httpBackendDecorator);
        }])

        .run(['$httpBackend', function ($httpBackend) {

            for (var url in api_mock_data) {
                $httpBackend.whenGET(url).respond(api_mock_data[url]);
            }
        }]);
});
