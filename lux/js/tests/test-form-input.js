import {module, compile, getForm, _} from './tools';
import * as lux from '../index';


describe('lux form input', function() {

    beforeEach(() => {
        module('lux.form');
    });

    it('Test $lux', () => {

        var json = _.toJson({
            type: 'form',
            children: [
                {
                    type: 'text',
                    name: 'slug',
                    required: true,
                    minlength: 3,
                    maxlength: 8
                }
            ]
        });

        var element = compile(`<div><lux-form json=${json}></lux-form></div>`),
            form = getForm(element),
            scope = form.scope(),
            input = lux.querySelector(form, 'input'),
            dfield = scope.luxform.fields.slug;

        expect(_.isObject(dfield)).toBe(true);
        expect(input.length).toBe(1);
        expect(dfield.ngField).toBe(scope.form.slug);

        var field = scope.form.slug;

        field.$setViewValue('fooo');
        scope.$digest();
        expect(field.$valid).toBe(true);
        expect(field.$invalid).toBe(false);

        field.$setViewValue('fo');
        scope.$digest();
        expect(field.$valid).toBe(false);
        expect(field.$invalid).toBe(true);

        field.$setViewValue('fo78ghtyo');
        scope.$digest();
        expect(field.$valid).toBe(false);
        expect(field.$invalid).toBe(true);

        field.$setViewValue('12345678');
        scope.$digest();
        expect(field.$valid).toBe(true);
        expect(field.$invalid).toBe(false);
    });
});
