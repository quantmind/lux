define(function(require) {

    describe("Test lux.grid.dataProviderREST module", function() {

        var GridDataProviderREST;
        var apiMock;
        var listener;
        var dataProvider;
        var target = { url: 'dummy://url'};
        var subPath = 'dummy/subPath';
        var gridState = { dummy: 'gridstate' };
        var options = { dummy: 'options' };

        beforeEach(function () {
            apiMock = createLuxApiMock();
            var $luxMock = createLuxMock(apiMock);

            angular.mock.module('lux.grid.dataProviderREST', function($provide) {
                $provide.value('$lux', $luxMock);
            });

            inject(function (_GridDataProviderREST_) {
                GridDataProviderREST = _GridDataProviderREST_;
            });

            listener = {
                onMetadataReceived: jasmine.createSpy(),
                onDataReceived: jasmine.createSpy()
            };

            dataProvider = new GridDataProviderREST(target, subPath, gridState, listener);
        });

        afterEach(function () {
        });

        it('connect() calls $lux.api get() with URL and success callback; when $lux.api calls this callback, it calls onMetadataReceived. Then it calls get() again with gridState', function() {
            dataProvider.connect();

            expect(apiMock.get).toHaveBeenCalledWith({ path: 'dummy/subPath/metadata' });

            var onMetadataReceivedSuccessCallback = apiMock.success.calls.all()[0].args[0];
            onMetadataReceivedSuccessCallback('metadata');

            expect(listener.onMetadataReceived).toHaveBeenCalledWith('metadata');

            expect(apiMock.get).toHaveBeenCalledWith({ path: subPath }, gridState);

            var onDataReceivedSuccessCallback = apiMock.success.calls.all()[1].args[0];
            onDataReceivedSuccessCallback('data');

            expect(listener.onDataReceived).toHaveBeenCalledWith('data');

        });

        it('getPage() calls $lux.api get() with {}, options and success callback; when $lux.api calls this callback, it passes data to onDataReceived', function() {
            dataProvider.getPage(options);

            expect(apiMock.get).toHaveBeenCalledWith({}, options);

            var onDataReceivedSuccessCallback = apiMock.success.calls.all()[0].args[0];
            onDataReceivedSuccessCallback('data');

            expect(listener.onDataReceived).toHaveBeenCalledWith('data');
        });

        it('deleteItem() calls $lux.api delete() with URL; success and error callbacks passed along.', function() {
            var identifier = 'my ID';
            var onSuccess = function() {};
            var onFailure = function() {};

            dataProvider.deleteItem(identifier, onSuccess, onFailure);

            expect(apiMock.delete).toHaveBeenCalledWith({ path: subPath + '/' + identifier});
            expect(apiMock.success).toHaveBeenCalledWith(onSuccess);
            expect(apiMock.error).toHaveBeenCalledWith(onFailure);
        });
/*
        it('destroy() disables data provider', function() {

        });
*/
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