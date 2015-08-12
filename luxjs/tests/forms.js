
    describe("Test lux.form module", function() {
        //
        lux.formTests = {};

        // Utility for creating a JSON form for testing
        function createForm() {
            var form = {
                field: {
                    type: 'form'
                },
                children: []
            };
            lux.forEach(arguments, function (attrs) {
                form['children'].push({field: attrs});
            });
            return form;
        }

        function digest ($compile, $rootScope, template) {
            var scope = $rootScope.$new(),
                element = $compile(template)(scope);
            scope.$digest();
            return element;
        }

        beforeEach(function () {
            module('lux.form');
        });

        it("simple form - one input", inject(function($compile, $rootScope) {
            lux.formTests.simple = createForm({type: 'text', name: 'body'});
            var element = digest($compile, $rootScope,
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
            lux.formTests.select = createForm({
                type: 'select',
                name: 'choice',
                required: true,
                options: ['one', 'two', 'three']
            });

            var element = digest($compile, $rootScope,
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

        it("select input + widget", inject(function($compile, $rootScope, formDefaults) {
            lux.formTests.select = createForm({
                type: 'select',
                name: 'choice',
                required: true,
                options: ['one', 'two', 'three']
            });

            formDefaults.select.widget = {
                name: 'selectUI',
                enableSearch: true,
                theme: 'bootstrap'
            };

            var element = digest($compile, $rootScope,
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
            expect(tags[1].tagName).toBe('UI-SELECT');
            expect(tags[1].getAttribute('theme')).toBe('bootstrap');

            var select = lux.$(tags[1]),
                options = select.children();
            expect(options.length).toBe(2);
            //
        }));
    });
