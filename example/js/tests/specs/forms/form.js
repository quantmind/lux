define(['angular',
        'lux',
        'lux/testing',
        'tests/mocks/lux',
        'lux/forms'], function (angular, lux, tests) {
    'use strict';

    describe('Test lux.form module', function() {

        lux.formTests = {};

        beforeEach(function () {
            module('lux.form');
        });

        it('check lux.forms', function () {
            expect(angular.isObject(lux.forms)).toBe(true);
        });

        it('on success, email validate', function () {
            lux.formTests.vForm2 = tests.createForm([{
                type: 'email',
                name: 'login',
                required: true
            }]);

            var element = tests.compile('<div><lux-form data-options="lux.formTests.vForm2"></lux-form></div>'),
                form = element.find('form'),
                scope = form.scope();

            scope.form.login.$setViewValue('user@example.com');
            scope.$digest();
            expect(scope.form.login.$valid).toBe(true);
            expect(scope.form.login.$invalid).toBe(false);
        });

        it('on failure, email validate', function () {
            lux.formTests.vForm3 = tests.createForm({
                type: 'email',
                name: 'login',
                required: true
            });

            var element = tests.compile('<div><lux-form data-options="lux.formTests.vForm3"></lux-form></div>'),
                form = element.find('form'),
                scope = form.scope();

            scope.form.login.$setViewValue('example.com');
            scope.$digest();
            expect(scope.form.login.$valid).toBe(false);
            expect(scope.form.login.$invalid).toBe(true);
        });

        it('submit empty email field', function () {
            lux.formTests.vForm4 = tests.createForm({
                type: 'email',
                name: 'login',
                required: true
            });

            var element = tests.compile('<div><lux-form data-options="lux.formTests.vForm4"></lux-form></div>');
            var form = element.find('form');
            var validators = form.find('span');
            var scope = element.scope();

            // Submit empty field
            scope.form.login.$setViewValue('');
            scope.form.$setSubmitted(true);
            scope.$digest();
            expect(validators.eq(0).hasClass('ng-hide')).toBe(false);
            expect(validators.eq(1).hasClass('ng-hide')).toBe(true);
            expect(validators.eq(2).hasClass('ng-hide')).toBe(true);
        });

        it('submit valid email field', function () {
            lux.formTests.vForm5 = tests.createForm([{
                type: 'email',
                name: 'login',
                required: true
            }]);

            var element = tests.compile('<div><lux-form data-options="lux.formTests.vForm5"></lux-form></div>');

            var _form = angular.element(element).find('form');
            var validators = _form.find('span');
            var scope = _form.scope();

            // Submit invalid email (angular validation)
            scope.form.login.$setViewValue('test@example.com');
            scope.form.$setSubmitted(true);
            scope.$digest();
            expect(validators.eq(0).hasClass('ng-hide')).toBe(true);
            expect(validators.eq(1).hasClass('ng-hide')).toBe(true);
            expect(validators.eq(2).hasClass('ng-hide')).toBe(true);
        });

        it('submit invalid email field', function () {
            lux.formTests.vForm6 = tests.createForm([{
                type: 'email',
                name: 'login',
                required: true
            }]);

            var element = tests.compile('<div><lux-form data-options="lux.formTests.vForm6"></lux-form></div>'),
                form = element.find('form'),
                scope = form.scope(),
                validators = form.find('span');

            // Submit invalid email (angular validation)
            scope.form.login.$setViewValue('invalid_email');
            scope.$digest();
            expect(validators.eq(0).hasClass('ng-hide')).toBe(true);
            expect(validators.eq(1).hasClass('ng-hide')).toBe(false);
            expect(validators.eq(2).hasClass('ng-hide')).toBe(true);
            scope.form.$setSubmitted();
            expect(validators.eq(0).hasClass('ng-hide')).toBe(true);
            expect(validators.eq(1).hasClass('ng-hide')).toBe(false);
            expect(validators.eq(2).hasClass('ng-hide')).toBe(true);
        });


        it('should set correct renderer function for the checkbox field', function () {
            lux.formTests.vForm7 = tests.createForm([{
                type: 'checkbox',
                element: 'input',
                name: 'is_active'
            }]);

            var element = tests.compile('<div><lux-form data-options="lux.formTests.vForm7"></lux-form></div>');

            // Check if input is inside of label tag.
            var label = angular.element(element).find('label').eq(0);
            expect(label.find('input')[0].tagName).toBe('INPUT');
            expect(label.find('input').eq(0).attr('type')).toBe('checkbox');
        });

    });

});
