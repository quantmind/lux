import {module, compile, _} from './tools';
import * as lux from '../';


describe('Test lux.nav -', function () {
    //
    var t = window._navbar_tests_ = {};


    beforeEach(function () {
        module('lux.nav');
    });

    it('directive', function () {
        var template = '<lux-navbar theme="inverse" data-id="navid3" top=1></lux-navbar>',
            element = compile(template);

        expect(element.children().length).toBe(1);
        var nav = _.element(element.children()[0]);
        //
        expect(nav.length).toBe(1);
        expect(nav[0].tagName).toBe('NAV');
        expect(nav.hasClass('navbar')).toBe(true);
        expect(nav.hasClass('navbar-inverse')).toBe(true);
        expect(nav.hasClass('navbar-static-top')).toBe(true);
        expect(nav.hasClass('navbar-fixed-top')).toBe(false);
        expect(nav.attr('id')).toBe('navid3');
    });

    it('directive with options from object', function () {
        t.navbar1 = {
            id: 'navbar1',
            theme: 'inverse',
            top: true,
            fixed: true,
            itemsRight: [
                {href: '/', name: 'home'},
                {href: '/bla', name: 'bla'}
            ]
        };
        var template = '<lux-navbar navbar="_navbar_tests_.navbar1"></lux-navbar>',
            element = compile(template),
            nav = _.element(element.children()[0]);
        //
        expect(nav.length).toBe(1);
        expect(nav[0].tagName).toBe('NAV');
        expect(nav.hasClass('navbar')).toBe(true);
        expect(nav.hasClass('navbar-inverse')).toBe(true);
        expect(nav.hasClass('navbar-static-top')).toBe(true);
        expect(nav.hasClass('navbar-fixed-top')).toBe(true);
        expect(nav.attr('id')).toBe('navbar1');
        //
        var right = lux.querySelector(nav, '.navbar-right');
        expect(right.length).toBe(1);
        expect(right.children().length).toBe(2);
        _.forEach(right.children(), (child) => {
            var li = _.element(child);
            expect(li[0].tagName).toBe('LI');
            expect(li.children().length).toBe(1);
        });
    });

});
