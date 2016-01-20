define(['angular',
        'lux',
        'tests/mocks/utils',
        'lux/nav'], function (angular, lux, tests) {
    'use strict';

    describe('Test sidebar', function () {
        //
        beforeEach(function () {
            module('lux.sidebar');
        });

        it('sidebar + navbar with user check: directive defaults',
            inject(function ($compile, $rootScope) {
                var element = tests.digest($compile, $rootScope, '<sidebar></sidebar>');
                //
                expect(element[0].tagName).toBe('SIDEBAR');
                //
                var nav = angular.element(element.children()[0]);
                //
                expect(nav[0].tagName).toBe('NAV');
                expect(nav.hasClass('navbar')).toBe(true);

                if ($rootScope.user) {
                    var sidebar = angular.element(element.children()[1]);

                    expect(element.children().length).toBe(2);
                    expect(sidebar[0].tagName).toBe('ASIDE');
                    expect(sidebar.hasClass('main-sidebar')).toBe(true);
                    expect(sidebar.attr('id')).toBe('');
                } else {
                    expect(element.children().length).toBe(1);
                }
            })
        );


        it('sidebar + navbar directive with data',
            inject(function ($compile, $rootScope) {
                var template = '<sidebar data-position="left" data-id="sidebar1"></navbar>',
                    element = tests.digest($compile, $rootScope, template),
                    body = angular.element('body');
                //
                if ($rootScope.user) {
                    var sidebar = angular.element(element.children()[1]);

                    expect(element.children().length).toBe(2);
                    expect(sidebar[0].tagName).toBe('ASIDE');
                    expect(sidebar.attr('id')).toBe('sidebar1');
                    expect(body.hasClass('left-sidebar')).toBe(true);
                } else {
                    expect(element.children().length).toBe(1);
                }
            })
        );

        it('sidebar + navbar directive with options from object',
            inject(function ($compile, $rootScope) {
                lux.context._sidebar = {
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
                var template = '<sidebar data-options="lux.context._sidebar"></sidebar>',
                    element = tests.digest($compile, $rootScope, template),
                    body = angular.element('body');
                delete lux.context._sidebar;
                //
                if ($rootScope.user) {
                    var sidebar = angular.element(element.children()[1]);

                    expect(element.children().length).toBe(2);
                    expect(sidebar[0].tagName).toBe('ASIDE');
                    expect(sidebar.hasClass('main-sidebar')).toBe(true);
                    expect(sidebar.attr('id')).toBe('sidebar1');
                    expect(body.hasClass('right-sidebar')).toBe(true);
                } else {
                    expect(element.children().length).toBe(1);
                }
            })
        );

    });

});
