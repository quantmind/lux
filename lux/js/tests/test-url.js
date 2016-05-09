import {urlJoin} from '../core/urls';


describe('lux core', function() {

    it('urlJoin', function () {
        expect(urlJoin('bla', 'foo')).toBe('bla/foo');
        expect(urlJoin('bla/', '/foo')).toBe('bla/foo');
        expect(urlJoin('bla', '')).toBe('bla');
        expect(urlJoin('bla', '///foo')).toBe('bla/foo');
        expect(urlJoin('bla//////', '///foo')).toBe('bla/foo');
    });
});
