define(['angular',
        'angular-mocks'], function(angular) {
    'use strict';

    angular.module('lux.mocks.window', [])
        .factory('$window', [function () {
            return {
                location: {
                    pathname: '/tests',
                    toString: function () {
                        return 'http://jasmine.com/tests';
                    }
                }
            };
        }]);
});
