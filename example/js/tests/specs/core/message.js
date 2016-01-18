define(['angular',
        'lux/message',
        'tests/mocks/utils'], function (angular, lux, utils) {
    'use strict';

    beforeEach(function () {
        module('lux.message');
    });

    describe('Messages', function () {

        it('messages directive', inject(function($compile, $rootScope) {
            var template = '<messages></messages>',
                element = utils.digest($compile, $rootScope, template),
                scope = element.scope();

            expect(element[0].tagName).toBe('DIV');
            expect(scope.messages.length).toBe(0);
        }));

    });

});
