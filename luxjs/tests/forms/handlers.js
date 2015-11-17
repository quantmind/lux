define(function(require) {

    describe("Test lux.form.handlers module", function() {

        var $lux;
        var successMessageSpy;
        var errorMessageSpy;

        beforeEach(function () {
            apiMock = createLuxApiMock();
            var $luxMock = createLuxMock(apiMock);

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

    // Function.prototype.bind polyfill
    // PhantomJS has no Function.prototype.bind method
    if (!Function.prototype.bind) {
    Function.prototype.bind = function(oThis) {
        if (typeof this !== 'function') {
            // closest thing possible to the ECMAScript 5
            // internal IsCallable function
            throw new TypeError('Function.prototype.bind - what is trying to be bound is not callable');
        }

        var aArgs   = Array.prototype.slice.call(arguments, 1),
            fToBind = this,
            fNOP    = function() {},
            fBound  = function() {
                return fToBind.apply(this instanceof fNOP ? this : oThis, aArgs.concat(Array.prototype.slice.call(arguments)));
            };

        if (this.prototype) {
            // native functions don't have a prototype
            fNOP.prototype = this.prototype;
        }
        fBound.prototype = new fNOP();
            return fBound;
        };
    }


});