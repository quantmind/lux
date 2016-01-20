define(['angular',
        'lux',
        'tests/mocks/utils',
        'lux/forms'], function (angular, lux, tests) {
    'use strict';

    lux.formFieldTests = {};


    describe('Test lux.form fields', function () {

        beforeEach(function () {
            module('lux.form');
        });

        it('simple form - one input',
            inject(function ($compile, $rootScope) {
                lux.formFieldTests.simple = tests.createForm([{
                    type: 'text',
                    name: 'body'
                }]);
                var element = tests.digest($compile, $rootScope,
                    '<div><lux-form data-options="lux.formFieldTests.simple"></lux-form></div>'),
                    form = element.children();
                //
                expect(form.length).toBe(1);
                expect(form[0].tagName).toBe('FORM');
                expect(form.children().length).toBe(1);
                expect(form.children()[0].tagName).toBe('DIV');
                //
                var tags = form.children().children();
                expect(tags[0].tagName).toBe('LABEL');
                expect(tags[1].tagName).toBe('INPUT');
                //
            })
        );

        it('select input',
            inject(function ($compile, $rootScope) {
                lux.formFieldTests.select = tests.createForm([{
                    type: 'select',
                    name: 'choice',
                    required: true,
                    options: ['one', 'two', 'three']
                }]);

                var element = tests.digest($compile, $rootScope,
                    '<div><lux-form data-options="lux.formFieldTests.select"></lux-form></div>'),
                    form = element.children();
                //
                expect(form.length).toBe(1);
                expect(form[0].tagName).toBe('FORM');
                expect(form.children().length).toBe(1);
                expect(form.children()[0].tagName).toBe('DIV');
                //
                var tags = form.children().children();
                expect(tags[0].tagName).toBe('LABEL');
                expect(tags[1].tagName).toBe('SELECT');

                var select = angular.element(tags[1]),
                    options = select.children();
                expect(options.length).toBe(4);
                //
            }));

    });

    describe('Test lux.form with date field', function () {

        beforeEach(function () {
            module('lux.form');
        });

        it('convert model from date string into date object', inject(function ($compile, $rootScope) {
            lux.formFieldTests.date = lux.tests.createForm([{
                type: 'date',
                name: 'date'
            }]);
            var element = lux.tests.digest($compile, $rootScope,
                '<div><lux-form data-options="lux.formFieldTests.date"></lux-form></div>');
            //
            var form = angular.element(element).find('form');
            var field = form.find('input').eq(0);

            var scope = form.scope();
            scope.form.date.$setViewValue('2011-04-02');
            scope.$digest();

            expect(field.attr('name')).toEqual('date');
            expect(field.attr('type')).toEqual('date');
            expect(scope.form.date.$modelValue instanceof Date).toBeTruthy();
            //
        }));
    });

});
