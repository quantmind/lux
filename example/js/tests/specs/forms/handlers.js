define(['angular',
        'lux',
        'tests/mocks/lux',
        'lux/forms'], function (angular, lux) {
    'use strict';

    describe('Test lux.form.handlers module', function() {

        var $lux;
        var successMessageSpy;
        var errorMessageSpy;

        beforeEach(function () {
            var $luxMock = lux.mocks.$lux();

            angular.mock.module('lux.form.handlers', function($provide) {
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

        it('Creates a $lux.formHandlers object', function() {
            expect(angular.isObject($lux.formHandlers)).toBe(true);
            expect(angular.isArray($lux.formHandlers)).toBe(false);
        });

        it('Creates $lux.formHandlers.reload method', function() {
            expect(typeof $lux.formHandlers.reload).toBe('function');
        });

        it('Creates $lux.formHandlers.redirectHome method', function() {
            expect(typeof $lux.formHandlers.redirectHome).toBe('function');
        });

        it('Creates $lux.formHandlers.login method', function() {
            expect(typeof $lux.formHandlers.login).toBe('function');
        });

        it('Creates $lux.formHandlers.passwordRecovery method', function() {
            expect(typeof $lux.formHandlers.passwordRecovery).toBe('function');
        });

        it('Creates $lux.formHandlers.passwordChanged method', function() {
            expect(typeof $lux.formHandlers.passwordChanged).toBe('function');
        });

        it('Creates $lux.formHandlers.enquiry method', function() {
            expect(typeof $lux.formHandlers.enquiry).toBe('function');
        });

        it('on success, $lux.formHandlers.enquiry method displays success message', function() {
            var mockResponse = {
                data: {
                    success: true
                }
            };

            $lux.formHandlers.enquiry(mockResponse);

            expect(successMessageSpy).toHaveBeenCalledWith(jasmine.any(String));
        });

        it('on failure, $lux.formHandlers.enquiry method displays failure message', function() {
            var mockResponse = {
                data: {
                    success: false
                }
            };

            $lux.formHandlers.enquiry(mockResponse);

            expect(errorMessageSpy).toHaveBeenCalledWith(jasmine.any(String));
        });

    });

});
