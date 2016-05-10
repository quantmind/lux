import {module, compile, getForm, _} from './tools';
import * as lux from '../index';


describe('lux core', function() {

    beforeEach(() => {
        module('lux.form');
    });

    it('Test $lux', () => {

        var json = _.toJson({
            children: [
                {
                    type: 'email',
                    name: 'login',
                    required: true
                }
            ]
        });

        var element = compile(`<div><lux-form json=${json}></lux-form></div>`),
            form = getForm(element),
            scope = form.isolateScope(),
            input = lux.querySelector(form, 'input');

        expect(_.isObject(scope.info.fields['login'])).toBe(true);
        expect(input.length).toBe(1);

        //scope.model.login = 'user@example.com';
        //scope.$digest();
        scope.form.login.$setViewValue('user@example.com');
        scope.$digest();
        expect(scope.form.login.$valid).toBe(true);
        expect(scope.form.login.$invalid).toBe(false);
    });
});
