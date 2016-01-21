/* eslint angular/no-private-call: [2,{"allow":["$$hashKey"]}] */
define(['angular',
        'lux',
        'angular-mocks'], function (angular) {
    'use strict';

    angular.module('lux.utils.test', ['lux.services', 'ngMockE2E'])

        .run(['luxHttpPromise', '$httpBackend', function (luxHttpPromise, $httpBackend) {
            //
            extendHttpPromise(luxHttpPromise, $httpBackend);
        }])
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


    function extendHttpPromise (luxHttpPromise, $httpBackend) {

        luxHttpPromise.expect = function (data, status) {
            var promise = this,
                done = false,
                options = promise.options();
            $httpBackend.expect(options.method.toUpperCase(), options.url).respond(status);

            promise.then(function (d, headers) {
                done = true;
                if (angular.isFunction(data))
                    data(d, headers);
                else
                    expect(d).toEqual(data);
            });

            $httpBackend.flush(1, true);
            expect(done).toBe(true);
        };
    }

});