define(['angular',
        'tests/data/restapi',
        'lux/testing'], function (angular, api_mock_data) {
    'use strict';

    angular.module('lux.mocks.http', ['lux.utils.test'])

        .run(['$httpBackend', function ($httpBackend) {
            for (var url in api_mock_data) {
                $httpBackend.whenGET(url).respond(function () {
                    return api_mock_data[url];
                });
            }
        }]);

});
