define(['angular',
        'lux',
        'tests/mocks/utils',
        'lux/forms'], function (angular, lux) {
    'use strict';

    lux.formTests = {};


    describe('Test lux.form module', function () {

        beforeEach(function () {
            module('lux.form');
        });

        it('simple form - one input', inject(function ($compile, $rootScope) {
            lux.formTests.simple = lux.tests.createForm([{
                type: 'text',
                name: 'body'
            }]);
            var element = lux.tests.digest($compile, $rootScope,
                '<div><lux-form data-options="lux.formTests.simple"></lux-form></div>'),
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
        }));

        it('select input', inject(function ($compile, $rootScope) {
            lux.formTests.select = lux.tests.createForm([{
                type: 'select',
                name: 'choice',
                required: true,
                options: ['one', 'two', 'three']
            }]);

            var element = lux.tests.digest($compile, $rootScope,
                '<div><lux-form data-options="lux.formTests.select"></lux-form></div>'),
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


    describe('Test lux.form with selectUI', function () {

        // Angular module for select-UI forms
        angular.module('lux.form.test.select.ui', ['lux.form'])

            .factory('formElements', ['defaultFormElements', function (defaultFormElements) {
                return function () {
                    var elements = defaultFormElements();
                    elements.select.widget = {
                        name: 'selectUI',
                        enableSearch: true,
                        theme: 'bootstrap'
                    };
                    return elements;
                };
            }]);
        //
        lux.formSelectUITests = {};

        beforeEach(function () {
            module('lux.form.test.select.ui');
        });

        it('select input + widget', inject(function ($compile, $rootScope) {

            lux.formSelectUITests.select = lux.tests.createForm([{
                type: 'select',
                name: 'choice',
                required: true,
                options: ['one', 'two', 'three']
            }]);

            var element = lux.tests.digest($compile, $rootScope,
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

    describe('Test lux.form with file field', function () {

        beforeEach(function () {
            module('lux.form');
        });

        it('adds the ngf-select directive', inject(function ($compile, $rootScope) {
            lux.formTests.file = lux.tests.createForm([{
                type: 'file',
                name: 'file'
            }]);
            var element = lux.tests.digest($compile, $rootScope,
                '<div><lux-form data-options="lux.formTests.file"></lux-form></div>'),
                form = element.children();
            //
            expect(form.children().length).toBe(1);
            //
            var tags = form.children().children();
            expect(tags[0].tagName).toBe('LABEL');
            expect(tags[1].tagName).toBe('INPUT');
            expect(tags[1].getAttribute('type')).toBe('file');
            expect(tags[1].hasAttribute('ngf-select')).toBeTruthy();
            //
        }));

        it('doesnt adds the ngf-select directive', inject(function ($compile, $rootScope) {
            lux.formTests.fileNoNgf = lux.tests.createForm([{
                type: 'file',
                name: 'file'
            }], {useNgFileUpload: false});
            var element = lux.tests.digest($compile, $rootScope,
                '<div><lux-form data-options="lux.formTests.fileNoNgf"></lux-form></div>'),
                form = element.children();
            //
            expect(form.children().length).toBe(1);
            //
            var tags = form.children().children();
            expect(tags[0].tagName).toBe('LABEL');
            expect(tags[1].tagName).toBe('INPUT');
            expect(tags[1].getAttribute('type')).toBe('file');
            expect(tags[1].hasAttribute('ngf-select')).toBeFalsy();
            //
        }));
    });

    describe('Test lux.form with date field', function () {

        beforeEach(function () {
            module('lux.form');
        });

        it('convert model from date string into date object', inject(function ($compile, $rootScope) {
            lux.formTests.date = lux.tests.createForm([{
                type: 'date',
                name: 'date'
            }]);
            var element = lux.tests.digest($compile, $rootScope,
                '<div><lux-form data-options="lux.formTests.date"></lux-form></div>');
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
