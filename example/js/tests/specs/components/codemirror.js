define(['angular',
        'lux/testing',
        'lux/components/codemirror'], function (angular, tests) {
    'use strict';

    describe('Test lux.codemirror module', function () {

        beforeEach(function () {
            module('lux.codemirror');
        });

        it('Should have a child element with a div.CodeMirror', function (done) {
            // Explicit a parent node to support the directive.
            var element = tests.compile('<div lux-codemirror></div>'),
                scope = element.scope();

            scope.$on('CodeMirror', function () {
                element = element.children();
                expect(element).toBeDefined();
                expect(element.prop('tagName')).toBe('DIV');
                expect(element.prop('classList').length).toEqual(3);
                expect(element.prop('classList')[0]).toEqual('CodeMirror');
                expect(element.prop('classList')[1]).toEqual('cm-s-monokai');
                done();
            });

        });

        it('Default mode is markdown', function(done) {
            var element = tests.compile('<div lux-codemirror></div>'),
                scope = element.scope();

            scope.$on('CodeMirror', function (e, cm) {
                expect(cm).toBe(scope.cm);
                expect(e.name).toBe('CodeMirror');
                expect(cm.options.mode).toEqual('markdown');
                done();
            });

        });

        it('Set mode to htmlmixed', function(done) {
            var options = angular.toJson({mode: 'html'}),
                element = tests.compile("<div lux-codemirror='" + options + "'></div>"),
                scope = element.scope();

            scope.$on('CodeMirror', function (e, cm) {
                expect(cm.getOption('mode')).toEqual('htmlmixed');
                done();
            });
        });


        it('when the text changes should update the model', function(done) {
            var element = tests.compile('<div lux-codemirror ng-model="foo"></div>'),
                scope = element.scope();

            scope.$on('CodeMirror', function(e, cm) {
                var ctrl = element.controller('ngModel');
                expect(ctrl.$pristine).toBe(true);
                expect(ctrl.$valid).toBe(true);

                var value = 'baz';
                cm.setValue(value);
                scope.$apply();
                expect(scope.foo).toBe(value);

                expect(ctrl.$valid).toBe(true);
                expect(ctrl.$dirty).toBe(true);
                done();
            });
        });

        it('When the model changes should update the text', function(done) {
            var element = tests.compile('<div lux-codemirror ng-model="foo"></div>'),
                scope = element.scope();

            scope.$on('CodeMirror', function(e, cm) {
                var ctrl = element.controller('ngModel');
                expect(ctrl.$pristine).toBe(true);
                expect(ctrl.$valid).toBe(true);

                scope.$apply('foo = "bar"');
                expect(cm.getValue()).toBe(scope.foo);

                expect(ctrl.$pristine).toBe(true);
                expect(ctrl.$valid).toBe(true);
                done();
            });
        });
    });

});
