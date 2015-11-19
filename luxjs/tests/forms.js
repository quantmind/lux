 // Utility for creating a JSON form for testing
    var testFormUtils = {
        createForm: function (children, formAttrs) {
            var form = {
                field: {
                    type: 'form'
                },
                children: []
            };
            angular.extend(form.field, formAttrs);
            lux.forEach(children, function (attrs) {
                form['children'].push({field: attrs});
            });
            return form;
        },
        digest: function ($compile, $rootScope, template) {
            var scope = $rootScope.$new(),
                element = $compile(template)(scope);
            scope.$digest();
            return element;
        }
    };

    describe("Test lux.form module", function() {
        lux.formTests = {};

        beforeEach(function () {
            module('lux.form');
        });

        it("simple form - one input", inject(function($compile, $rootScope) {
            lux.formTests.simple = testFormUtils.createForm([{type: 'text', name: 'body'}]);
            var element = testFormUtils.digest($compile, $rootScope,
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

        it("select input", inject(function($compile, $rootScope) {
            lux.formTests.select = testFormUtils.createForm([{
                type: 'select',
                name: 'choice',
                required: true,
                options: ['one', 'two', 'three']
            }]);

            var element = testFormUtils.digest($compile, $rootScope,
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

            var select = lux.$(tags[1]),
                options = select.children();
            expect(options.length).toBe(3);
            //
        }));

    });


    describe("Test lux.form with selectUI", function() {

        // Angular module for select-UI forms
        angular.module('lux.form.test.selectui', ['lux.form'])

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
            module('lux.form.test.selectui');
        });

        it("select input + widget", inject(function($compile, $rootScope) {

            lux.formSelectUITests.select = testFormUtils.createForm([{
                type: 'select',
                name: 'choice',
                required: true,
                options: ['one', 'two', 'three']
            }]);

            var element = testFormUtils.digest($compile, $rootScope,
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

            var select = lux.$(tags[1]),
                options = select.children();
            expect(options.length).toBe(2);
            //
        }));
    });

    describe("Test lux.form with file field", function() {
        lux.formTests = {};

        beforeEach(function () {
            module('lux.form');
        });

        it("adds the ngf-select directive", inject(function($compile, $rootScope) {
            lux.formTests.file = testFormUtils.createForm([{type: 'file', name: 'file'}]);
            var element = testFormUtils.digest($compile, $rootScope,
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

        it("doesn't adds the ngf-select directive", inject(function($compile, $rootScope) {
            lux.formTests.fileNoNgf = testFormUtils.createForm([{type: 'file', name: 'file'}], {useNgFileUpload: false});
            var element = testFormUtils.digest($compile, $rootScope,
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

    describe("Test lux.form with date field", function() {
        lux.formTests = {};

        beforeEach(function () {
            module('lux.form');
        });

        it("adds the form-date directive", inject(function($compile, $rootScope) {
            lux.formTests.date = testFormUtils.createForm([{type: 'date', name: 'date'}]);
            var element = testFormUtils.digest($compile, $rootScope,
                '<div><lux-form data-options="lux.formTests.date"></lux-form></div>');
            //
            var form = angular.element(element).find('form');
            scope = form.scope();
            scope.form.date.$setViewValue('2011-04-02');
            scope.$digest();

            expect(form.find('input')[0].hasAttribute('format-date')).toBeTruthy();
            expect(scope.form.date.$modelValue instanceof Date).toBeTruthy();
            //
        }));
    });
