
    describe("Test lux.codemirror module", function() {

        var scope, $compile,
            cm = null,
            spies = angular.noop;

        beforeEach(function () {
            module('lux.codemirror');

            inject(function(_$rootScope_, _$compile_) {
                scope = _$rootScope_.$new();
                $compile = _$compile_;
            });

            var _constructor = window.CodeMirror;
            window.CodeMirror = jasmine.createSpy('window.CodeMirror')
                .and.callFake(function() {
                    cm = _constructor.apply(this, arguments);
                    spies(cm);
                    return cm;
                });

        });

        it('instance should be defined', function() {
            function compile() {
                $compile('<div lux-codemirror></div>')(scope);
            }

            expect(window.CodeMirror).toBeDefined();
        });

        it('should have a child element with a div.CodeMirror', function() {
            // Explicit a parent node to support the directive.
            var element = $compile('<div lux-codemirror></div>')(scope).children();

            expect(element).toBeDefined();
            expect(element.prop('tagName')).toBe('DIV');
            expect(element.prop('classList').length).toEqual(3);
            expect(element.prop('classList')[0]).toEqual('CodeMirror');
            expect(element.prop('classList')[1]).toEqual('cm-s-monokai');
        });

        it('default mode is markdown', function() {
            $compile('<div lux-codemirror"></div>')(scope);
            expect(cm.options.mode).toEqual('markdown');
        });

        it('set mode to htmlmixed', function() {
            $compile('<div lux-codemirror="{mode: \'html\'}"></div>')(scope);
            expect(cm.getOption('mode')).toEqual('htmlmixed');
        });


        it('when the text changes should update the model', function() {
            var element = $compile('<div lux-codemirror ng-model="foo"></div>')(scope);
            var ctrl = element.controller('ngModel');

            expect(ctrl.$pristine).toBe(true);
            expect(ctrl.$valid).toBe(true);

            var value = 'baz';
            cm.setValue(value);
            scope.$apply();
            expect(scope.foo).toBe(value);

            expect(ctrl.$valid).toBe(true);
            expect(ctrl.$dirty).toBe(true);

        });

        it('when the model changes should update the text', function() {
            var element = $compile('<div lux-codemirror ng-model="foo"></div>')(scope);
            var ctrl = element.controller('ngModel');

            expect(ctrl.$pristine).toBe(true);
            expect(ctrl.$valid).toBe(true);

            scope.$apply('foo = "bar"');
            expect(cm.getValue()).toBe(scope.foo);

            expect(ctrl.$pristine).toBe(true);
            expect(ctrl.$valid).toBe(true);
        });


    });




