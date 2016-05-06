import {module, inject, _} from './tools';
import '../index';


describe('lux.form', function() {
    let luxFormConfig;

    beforeEach(() => {
        module('lux.form');
    });

    beforeEach(inject((_luxFormConfig_) => {
        luxFormConfig = _luxFormConfig_;
    }));

    it('luxFormProvider object', () => {

        expect(_.isObject(luxFormConfig)).toBe(true);
        expect(_.isFunction(luxFormConfig.$get)).toBe(true);
        expect(_.isFunction(luxFormConfig.setType)).toBe(true);
        expect(_.isFunction(luxFormConfig.getType)).toBe(true);
    });

    it('luxFormProvider defaults', () => {

        var input = luxFormConfig.getType('input');
        expect(_.isObject(input)).toBe(true);
        expect(input.name).toBe('input');
    });
});
