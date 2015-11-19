define(function(require) {

    describe("Test lux.form module", function() {

        var $lux;
        var successMessageSpy;
        var errorMessageSpy;
        var scope;

        var testFormUtils = {
            createForm: function () {
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
            },
            digest: function ($compile, $rootScope, template) {
                scope = $rootScope.$new();
                var element = $compile(template)(scope);
                scope.$digest();
                return element;
            }
        };

        lux.formTests = {};

        beforeEach(function () {
            apiMock = createLuxApiMock();
            var $luxMock = createLuxMock(apiMock);

            angular.mock.module('lux.form', function($provide) {
                $provide.value('$lux', $luxMock);
            });

            inject(function (_$lux_) {
                $lux = _$lux_;
            });

            successMessageSpy = jasmine.createSpy();
            errorMessageSpy = jasmine.createSpy();

            $lux.messages = {};
            $lux.messages.success = successMessageSpy;
            $lux.messages.error = errorMessageSpy;
        });

        afterEach(function () {
        });

        it("should apply form-date directive to date input", inject(function($compile, $rootScope) {
            lux.formTests.simple = testFormUtils.createForm({
                type: 'date',
                name: 'birthDate'
            });

            var element = testFormUtils.digest($compile, $rootScope,
                '<div><lux-form data-options="lux.formTests.simple"></lux-form></div>');

            var form = angular.element(element).find('form');
            scope = form.scope();
            scope.form.birthDate.$setViewValue('2011-04-02');
            scope.$digest();

            expect(form.find('input')[0].hasAttribute('format-date')).toBe(true);
            expect(scope.form.birthDate.$modelValue instanceof Date).toBe(true);
        }));

        function createLuxMock(apiMock) {
            var $luxMock = {
                api: function() {
                    return apiMock;
                }
            };

            return $luxMock;
        }

        function createLuxApiMock() {
            var apiMock = {
                get: jasmine.createSpy(),
                delete: jasmine.createSpy(),
                success: jasmine.createSpy(),
                error: jasmine.createSpy()
            };

            apiMock.get.and.returnValue(apiMock);
            apiMock.delete.and.returnValue(apiMock);
            apiMock.success.and.returnValue(apiMock);
            apiMock.error.and.returnValue(apiMock);

            return apiMock;
        }
    });

});
