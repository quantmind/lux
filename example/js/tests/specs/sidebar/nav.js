define(['angular',
        'lux',
        'tests/mocks/utils',
        'lux/nav'], function (angular, lux, tests) {
    'use strict';

    describe('Test lux.nav module', function () {

        beforeEach(function () {
            module('lux.nav');
        });

        it('navbar directive', inject(function ($compile, $rootScope) {
            var template = '<navbar data-theme="inverse" data-id="navid3" data-top=1></navbar>',
                element = tests.digest($compile, $rootScope, template);

            expect(element.children().length).toBe(1);
            var nav = angular.element(element.children()[0]);
            //
            expect(nav[0].tagName).toBe('NAV');
            expect(nav.hasClass('navbar')).toBe(true);
            expect(nav.hasClass('navbar-inverse')).toBe(true);
            expect(nav.hasClass('navbar-static-top')).toBe(true);
            expect(nav.hasClass('navbar-fixed-top')).toBe(false);
            expect(nav.attr('id')).toBe('navid3');
        }));

        it('navbar directive with options from object', inject(function ($compile, $rootScope) {
            lux.context._navbar1 = {
                id: 'navbar1',
                theme: 'inverse',
                top: true,
                fixed: true,
                items: [{href: '/', name: 'home'},
                    {href: '/bla', name: 'bla'}]
            };
            var template = '<navbar data-options="lux.context._navbar1"></navbar>',
                element = tests.digest($compile, $rootScope, template),
                nav = angular.element(element.children()[0]);
            delete lux.context._navbar1;
            //
            expect(nav[0].tagName).toBe('NAV');
            expect(nav.hasClass('navbar')).toBe(true);
            expect(nav.hasClass('navbar-inverse')).toBe(true);
            expect(nav.hasClass('navbar-static-top')).toBe(true);
            expect(nav.hasClass('navbar-fixed-top')).toBe(true);
            expect(nav.attr('id')).toBe('navbar1');
        }));

    });

});
