import {module, compile, _} from './tools';
import '../';


describe('Test sidebar -', function () {
    //
    var t = window._sidebar_tests_ = {};

    beforeEach(function () {
        module('lux.nav');
    });

    it('sidebar + navbar with empty sidebar', function () {

        var element = compile('<lux-sidebar></lux-sidebar>'),
            scope = element.scope();
        //
        expect(element[0].tagName).toBe('LUX-SIDEBAR');
        expect(element.children().length).toBe(1);
        expect(_.isObject(scope.navbar)).toBe(true);
        //
        var navbar = _.element(element.children()[0]);
        //
        expect(navbar[0].tagName).toBe('LUX-NAVBAR');

        var nav = _.element(navbar.children()[0]);
        expect(nav[0].tagName).toBe('NAV');
        expect(nav.hasClass('navbar')).toBe(true);
    });

    it('sidebar + navbar directive with options from object', function () {
        t.sidebar1 = {
            id: 'sidebar11',
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
        var template = '<lux-sidebar sidebar="_sidebar_tests_.sidebar1"></lux-sidebar>',
            element = compile(template),
            scope = element.scope(),
            navbar = _.element(element.children()[0]),
            sidebar = _.element(element.children()[1]);

        expect(_.isObject(scope.navbar)).toBe(true);
        expect(_.isArray(scope.sidebars)).toBe(true);
        //
        expect(navbar[0].tagName).toBe('LUX-NAVBAR');
        //
        expect(sidebar[0].tagName).toBe('ASIDE');
        expect(sidebar.children().length).toBe(2);
        expect(sidebar.hasClass('sidebar')).toBe(true);
        expect(sidebar.hasClass('sidebar-right')).toBe(true);
        expect(sidebar.attr('id')).toBe('sidebar11');
    });

});
