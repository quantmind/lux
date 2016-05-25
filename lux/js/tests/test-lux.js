import {module, inject, _} from './tools';
import * as lux from '../index';


describe('lux core', function() {

    beforeEach(() => {
        module('lux');
    });

    it('Test version', () => {
        expect(_.isString(lux.version)).toBe(true);
    });

    it('Test $lux', inject(
        function($lux) {
            expect(_.isFunction($lux.$compile)).toBe(true);
            expect(_.isFunction($lux.$require)).toBe(true);
            expect(_.isFunction($lux.require)).toBe(true);
            expect(_.isObject($lux.context)).toBe(true);
            expect($lux.userToken).toBe(undefined);
            expect($lux.csrf).toBe(undefined);
        })
    );
});
