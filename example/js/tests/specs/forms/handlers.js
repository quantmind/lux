define(['angular',
        'lux',
        'lux/testing',
        'lux/forms'], function (angular, lux) {
    'use strict';

    describe('Test lux.form.handlers module', function() {
        var $lux, successMessageSpy, errorMessageSpy;

        beforeEach(function () {
            module('lux.form');

            inject(function (_$lux_) {
                $lux = _$lux_;
                successMessageSpy = jasmine.createSpy();
                errorMessageSpy = jasmine.createSpy();

                $lux.messages = {};
                $lux.messages.success = successMessageSpy;
                $lux.messages.error = errorMessageSpy;
            });
        });

        it('Creates a $lux.formHandlers object', function() {
            expect(angular.isObject($lux.formHandlers)).toBe(true);
            expect(angular.isArray($lux.formHandlers)).toBe(false);
        });

        it('Creates $lux.formHandlers.reload method', function() {
            expect(angular.isFunction($lux.formHandlers.reload)).toBe(true);
        });

        it('Creates $lux.formHandlers.redirectHome method', function() {
            expect(angular.isFunction($lux.formHandlers.redirectHome)).toBe(true);
        });

        it('Creates $lux.formHandlers.login method', function() {
            expect(angular.isFunction($lux.formHandlers.login)).toBe(true);
        });

        it('Creates $lux.formHandlers.passwordRecovery method', function() {
            expect(angular.isFunction($lux.formHandlers.passwordRecovery)).toBe(true);
        });

        it('Creates $lux.formHandlers.passwordChanged method', function() {
            expect(angular.isFunction($lux.formHandlers.passwordChanged)).toBe(true);
        });

        it('Creates $lux.formHandlers.enquiry method', function() {
            expect(angular.isFunction($lux.formHandlers.enquiry)).toBe(true);
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
