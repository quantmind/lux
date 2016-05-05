import {_, inject, module} from './tools';
import {joinUrl, getOptions} from '../core/utils';


describe('lux core', function() {

    beforeEach(() => {
        module('lux');
    });

    it('Check joinUrl', function () {
        expect(joinUrl('bla', 'foo')).toBe('bla/foo');
        expect(joinUrl('bla/', '/foo')).toBe('bla/foo');
        expect(joinUrl('bla', '')).toBe('bla');
        expect(joinUrl('bla', '///foo')).toBe('bla/foo');
        expect(joinUrl('bla//////', '///foo')).toBe('bla/foo');
    });

    it('Test getOptions', inject(
        function($window) {
            var t = $window._get_options_tests_ = {};
            let a = 1;

            t.v = a;
            expect(getOptions($window, {options: '_get_options_tests_.v', b: 4})).toBe(a);
            a = 'ciao';
            t.v = a;
            expect(getOptions($window, {options: '_get_options_tests_.v', b: 4})).toBe(a);
            a = {};
            t.v = a;
            expect(getOptions($window, {options: '_get_options_tests_.v', b: 4}).b).toBe(4);
        })
    );

    it('Test getOptions', inject(
        function($lux) {
            expect(_.isObject($lux.context)).toBe(true);
        })
    );
});
