
    describe("Test lux.form module", function() {
        //
        lux.formTests = {};

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

        var digest = function($compile, $rootScope, template) {
                var scope = $rootScope.$new(),
                    element = $compile(template)(scope);
                scope.$digest();
                return element;
            };

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
    });