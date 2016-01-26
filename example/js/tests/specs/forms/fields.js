define(['angular',
        'lux',
        'lux/testing',
        'lux/forms'], function (angular, lux, tests) {
    'use strict';

    lux.formFieldTests = {};


    describe('Test lux.form fields', function () {

        beforeEach(function () {
            module('lux.form');
        });

        it('text area', function () {
            lux.formFieldTests.simple = tests.createForm([{
                type: 'text',
                name: 'body'
            }]);
            var element = tests.compile('<div><lux-form data-options="lux.formFieldTests.simple"></lux-form></div>'),
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
        });

        it('email input', function() {
            lux.formTests.email1 = tests.createForm([{
                type: 'email',
                name: 'login',
                required: true
            }]);

            var element = tests.compile('<div><lux-form data-options="lux.formTests.email1"></lux-form></div>'),
                form = element.children();
            //
            var tags = form.children().children();
            expect(tags[0].tagName).toBe('LABEL');
            expect(tags[1].tagName).toBe('INPUT');

            expect(tags[1].required).toBe(true);
            expect(tags[1].type).toBe('email');
            expect(tags[1].name).toBe('login');
        });

        it('select input', function () {
            lux.formFieldTests.select = tests.createForm([{
                type: 'select',
                name: 'choice',
                required: true,
                options: ['one', 'two', 'three']
            }]);

            var element = tests.compile('<div><lux-form data-options="lux.formFieldTests.select"></lux-form></div>'),
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
            expect(options.length).toBe(3);
            //
        });

        it('date field', function () {
            lux.formFieldTests.date = lux.tests.createForm([{
                type: 'date',
                name: 'date'
            }]);
            var element = tests.compile('<div><lux-form data-options="lux.formFieldTests.date"></lux-form></div>'),
                scope = element.scope();
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
        });
    });

});
