/* eslint angular/no-private-call: [2,{"allow":["$$hashKey"]}] */
define(['angular',
        'lux',
        'angular-mocks'], function (angular, lux) {
    'use strict';

    lux.tests = {
        async: asyncTest
    };

    angular.module('lux.utils.test', ['lux.services', 'ngMockE2E'])

        .run(['luxHttpPromise', '$httpBackend', '$rootScope',
            function (luxHttpPromise, $httpBackend, $rootScope) {
                //
                extendHttpPromise(luxHttpPromise, $httpBackend, $rootScope);
            }]
        )
        //
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


    function extendHttpPromise (luxHttpPromise, $httpBackend, $rootScope) {

        luxHttpPromise.expect = function (data, headers, status) {
            var promise = this,
                done = false,
                options = promise.options();
            $httpBackend.expect(options.method.toUpperCase(), options.url);

            $rootScope.result = promise.then(function (d, headers) {
                done = true;
                if (angular.isFunction(data))
                    data(d, headers);
                else
                    expect(d).toEqual(data);
            });

            $httpBackend.flush();
            expect(done).toBe(true);
        };
    }

    return lux.tests;

    function asyncTest (before, testFunction) {
        var $timeout = angular.injector().get('$timeout');

        return test;

        function test () {
            $timeout(function () {
                var result = before();
                result.then(beforeDone);
            }, 1000);
        }

        function beforeDone (result) {
            if (testFunction) testFunction(result);
        }
    }
});
