define(['angular',
        'lux',
        'angular-mocks'], function (angular) {
    'use strict';

    angular.module('lux.utils.test', ['lux.services', 'ngMockE2E'])

        .factory('luxHttpTest', ['$lux', '$httpBackend', function ($lux, $httpBackend) {

            return {
                getOK: function (url, promise, callback) {
                    $httpBackend.whenGET(url).respond(200);
                    return httpExpect(promise, callback);
                }
            };

            function httpExpect (promise, callback) {
                var done = false;
                promise.then(function (data, headers) {
                    done = true;
                    callback(data, headers);
                });
                expect(done).toBe(true);
            }

        }]);

});