import {module, inject, compile} from './tools';
import '../index';


describe('lux core', function() {

    beforeEach(() => {
        module('lux.form');
    });

    it('Test $lux', inject(($rootScope) => {

        var scope = $rootScope.$new();

        scope.luxForm = {
            children: [
                {
                    type: 'email',
                    name: 'login',
                    required: true
                }
            ]
        };

        var element = compile('<div><lux-form></lux-form></div>', scope),
            form = element.find('form');

        expect(form.scope()).toBe(scope);

        scope.form.login.$setViewValue('user@example.com');
        scope.$digest();
        expect(scope.form.login.$valid).toBe(true);
        expect(scope.form.login.$invalid).toBe(false);
    }));
});
