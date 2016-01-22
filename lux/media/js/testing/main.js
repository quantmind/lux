/* eslint angular/no-private-call: [2,{"allow":["$$hashKey"]}] */
define(['angular',
        'lux',
        'angular-mocks'], function (angular, lux) {
    'use strict';

    lux.tests = {};

    angular.module('lux.utils.test', ['lux.services', 'ngMock'])

        .run(['luxHttpPromise', '$httpBackend',
            function (luxHttpPromise, $httpBackend) {
                //
                extendHttpPromise(luxHttpPromise, $httpBackend);
            }]
        );

    //
    //  Add the expect function to the promise
    function extendHttpPromise (luxHttpPromise, $httpBackend) {

        luxHttpPromise.expect = function (data) {
            var promise = this,
                done = false;

            promise.then(function (response) {
                done = true;
                if (angular.isFunction(data))
                    data(response.data, response.status, response.headers);
                else
                    expect(response.data).toEqual(data);
            });

            $httpBackend.flush();
            expect(done).toBe(true);
        };
    }

    return lux.tests;
});
