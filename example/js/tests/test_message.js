define(['angular',
        'lux/message/main',
        'lux/testing/main'], function (angular, lux, tests) {
    'use strict';

    beforeEach(function () {
        module('lux.message');
    });

    describe('Messages', function () {

        it('messages directive', function() {
            var element = tests.compile('<messages></messages>'),
                scope = element.scope();

            expect(element[0].tagName).toBe('DIV');
            expect(scope.messages.length).toBe(0);
        });

    });

});
