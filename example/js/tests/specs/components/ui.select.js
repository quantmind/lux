define(['angular',
        'lux',
        'tests/mocks/utils',
        'lux/components/ui.select'], function (angular, lux, tests) {
    'use strict';

    describe('Test lux.form with selectUI', function () {
        //
        lux.formSelectUITests = {};

        // Angular module for select-UI forms
        angular.module('lux.form.test.select.ui', ['lux.form.ui.select']);


        beforeEach(function () {
            module('lux.form.test.select.ui');
        });

        it('select input + widget', inject(function ($compile, $rootScope) {

            lux.formSelectUITests.select = tests.createForm([{
                type: 'select',
                name: 'choice',
                required: true,
                options: ['one', 'two', 'three']
            }]);

            var element = tests.digest($compile, $rootScope,
                '<div><lux-form data-options="lux.formSelectUITests.select"></lux-form></div>'),
                form = element.children();
            //
            expect(form.length).toBe(1);
            expect(form[0].tagName).toBe('FORM');
            expect(form.children().length).toBe(1);
            expect(form.children()[0].tagName).toBe('DIV');
            //
            var tags = form.children().children();
            expect(tags[0].tagName).toBe('LABEL');
            expect(tags[1].tagName).toBe('UI-SELECT');
            expect(tags[1].getAttribute('theme')).toBe('bootstrap');

            var select = angular.element(tags[1]),
                options = select.children();
            expect(options.length).toBe(2);
            //
        }));
    });

});
