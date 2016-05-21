import {module, compile, inject, _} from './tools';


describe('lux-crumbs directive', function() {
    var _location;

    beforeEach(() => {
        module('lux.cms');
    });

    beforeEach(inject(($location) => {
        _location = $location;
    }));

    it('Test lux-crumbs home', () => {

        var element = compile(`<lux-crumbs></lux-crumbs>`),
            scope = element.scope();

        expect(_.isObject(scope)).toBe(true);
        expect(_.isArray(scope.steps)).toBe(true);
        expect(scope.steps.length).toBe(1);
        expect(scope.steps[0].label).toBe('Home');
    });

    it('Test lux-crumbs', () => {
        _location.path('/bla/foo/extra');

        var element = compile(`<lux-crumbs></lux-crumbs>`),
            scope = element.scope();

        expect(_.isObject(scope)).toBe(true);
        expect(_.isArray(scope.steps)).toBe(true);
        expect(scope.steps.length).toBe(4);
        expect(scope.steps[0].label).toBe('Home');
        expect(scope.steps[0].href).toBe('/');
        expect(scope.steps[1].label).toBe('Bla');
        expect(scope.steps[1].href).toBe('/bla');
        expect(scope.steps[2].label).toBe('Foo');
        expect(scope.steps[2].href).toBe('/bla/foo');
        expect(scope.steps[3].label).toBe('Extra');
        expect(scope.steps[3].href).toBe('/bla/foo/extra');
    });
});
