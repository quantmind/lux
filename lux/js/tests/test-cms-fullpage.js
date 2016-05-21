import {module, compile, inject, _} from './tools';


describe('lux-fullpage directive', function() {
    var _window;

    beforeEach(() => {
        module('lux.cms');
    });

    beforeEach(inject(($window) => {
        _window = $window;
    }));

    it('Test lux-fullpage', () => {

        var element = compile(`<div lux-fullpage></div>`),
            scope = element.scope();

        expect(_.isObject(scope)).toBe(true);
        var height = element.css('min-height');
        expect(_.isString(height)).toBe(true);
        expect(height.length > 2).toBe(true);

    });

    it('Test lux-fullpage offset', () => {

        var element = compile(`<div lux-fullpage='{"offset": 80}'></div>`),
            wheight = _window.innerHeight;

        var height = element.css('min-height');
        expect(_.isString(height)).toBe(true);
        expect(height.length > 2).toBe(true);
        expect(height).toBe(wheight - 80 + 'px');

    });
});
