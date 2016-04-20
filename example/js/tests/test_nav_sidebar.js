define(['angular',
        'lux/main',
        'lux/testing/main',
        'lux/nav/main'], function (angular, lux, tests) {
    'use strict';

    describe('Test sidebar -', function () {
        //
        lux._sidebarTests = {};

        beforeEach(function () {
            module('lux.sidebar');
        });

        it('sidebar + navbar with user check: directive defaults', function () {

            var element = tests.compile('<sidebar></sidebar>'),
                scope = element.scope();
            //
            expect(element[0].tagName).toBe('SIDEBAR');
            //
            var nav = angular.element(element.children()[0]);
            //
            expect(nav[0].tagName).toBe('NAV');
            expect(nav.hasClass('navbar')).toBe(true);

            if (scope.user) {
                var sidebar = angular.element(element.children()[1]);

                expect(element.children().length).toBe(2);
                expect(sidebar[0].tagName).toBe('ASIDE');
                expect(sidebar.hasClass('main-sidebar')).toBe(true);
                expect(sidebar.attr('id')).toBe('');
            } else {
                expect(element.children().length).toBe(1);
            }
        });


        it('sidebar + navbar directive with data', function () {
            var template = '<sidebar data-position="left" data-id="sidebar1"></navbar>',
                element = tests.compile(template),
                scope = element.scope(),
                body = lux.querySelector('body');
            //
            if (scope.user) {
                var sidebar = angular.element(element.children()[1]);

                expect(element.children().length).toBe(2);
                expect(sidebar[0].tagName).toBe('ASIDE');
                expect(sidebar.attr('id')).toBe('sidebar1');
                expect(body.hasClass('left-sidebar')).toBe(true);
            } else {
                expect(element.children().length).toBe(1);
            }
        });

        it('sidebar + navbar directive with options from object', function () {
            lux._sidebarTests.sidebar1 = {
                id: 'sidebar1',
                position: 'right',
                collapse: true,
                toggle: false,
                sections: [{
                    name: 'Section1',
                    items: [{
                        name: 'Item1',
                        icon: 'fa fa-dashboard',
                        subitems: [
                            {
                                href: '#',
                                name: 'Dashbaord',
                                icon: 'fa fa-dashboard'
                            }
                        ]
                    }]
                }]
            };
            var template = '<sidebar data-options="lux._sidebarTests.sidebar1"></sidebar>',
                element = tests.compile(template),
                sidebar = angular.element(element.children()[1]);

            expect(sidebar[0].tagName).toBe('ASIDE');
            expect(sidebar.children().length).toBe(2);
            expect(sidebar.hasClass('sidebar')).toBe(true);
            expect(sidebar.hasClass('sidebar-right')).toBe(true);
            expect(sidebar.attr('id')).toBe('sidebar1');
        });

    });

});
