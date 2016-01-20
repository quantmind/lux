define(['angular',
        'tests/data/restapi',
        'angular-mocks'], function (angular, api_mock_data) {
    'use strict';

    angular.module('lux.mocks.http', ['ngMockE2E'])

        .run(['$httpBackend', function ($httpBackend) {

            for (var url in api_mock_data) {
                $httpBackend.whenGET(url).respond(api_mock_data[url]);
            }
        }]);
});
