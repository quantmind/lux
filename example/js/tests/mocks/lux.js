define(['angular',
        'lux',
        'tests/mocks/window',
        'tests/mocks/http'], function(angular) {
    'use strict';

    angular.module('lux.mocks.lux', ['lux.mocks.window', 'lux.mocks.http'])

        .factory('$lux', ['$window', function ($window) {
            var thenSpy = jasmine.createSpy();
            var luxApiMock = {
                get: jasmine.createSpy(),
                delete: jasmine.createSpy(),
                success: jasmine.createSpy(),
                error: jasmine.createSpy(),
                post: function() {
                    return {
                        then: function() {}
                    };
                }
            };
            luxApiMock.get.and.returnValue({
                then: thenSpy
            });

            var luxMock = {
                api: api,
                getLastThenSpy: getLastThenSpy,
                resetAllSpies: resetAllSpies,
                window: $window,
                formHandlers: {},
                getApiMock: getApiMock,
                getThenSpy: getThenSpy
            };

            function api() {
                return luxApiMock;
            }

            function getLastThenSpy() {
                return thenSpy;
            }

            function resetAllSpies() {
                thenSpy.calls.reset();
                luxApiMock.get.calls.reset();
            }

            function getApiMock() {
                return luxApiMock;
            }

            function getThenSpy() {
                return thenSpy;
            }

            return luxMock;
        }]);
});
