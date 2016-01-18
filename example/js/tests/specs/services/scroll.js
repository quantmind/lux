define(['angular',
        'lux/services/scroll'], function (angular) {
    'use strict';

    describe('Test lux.scroll module', function () {
        angular.module('lux.scroll.test', ['lux.loader', 'lux.scroll']);

        beforeEach(function () {
            module('lux.scroll.test');
        });

        it('Scroll scope defaults', inject(['$rootScope', function (scope) {
            var scroll = scope.scroll;
            expect(typeof(scroll)).toBe('object');
            expect(scroll.time).toBe(1);
            expect(scroll.offset).toBe(0);
            expect(scroll.frames).toBe(25);
        }]));

        it('Scroll scope overrides', function () {
            var context_override = {
                scroll: {
                    offset: 20,
                    frames: 15,
                    time: 0.5
                }
            };
            module(function ($provide) {
                $provide.value('context', context_override);
            });

            inject(['$rootScope', function ($rootScope) {
                var scope = $rootScope.$new();

                expect(typeof(scope.scroll)).toBe('object');
                expect(scope.scroll.time).toBe(0.5);
                expect(scope.scroll.offset).toBe(20);
                expect(scope.scroll.frames).toBe(15);
            }]);
        });

    });

});
