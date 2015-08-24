define(function(require) {

    describe("Test lux.grid.dataProviderWebsocket module", function() {

        var GridDataProviderWebsocket;
        var listener;
        var dataProvider;
        var websocketUrl = 'websocket://url';
        var scope = {};

        beforeEach(function () {
            angular.mock.module('lux.grid.dataProviderWebsocket', function ($provide) {
                $provide.value('$lux', {});
            });

            inject(function (_GridDataProviderWebsocket_, $rootScope) {
                GridDataProviderWebsocket = _GridDataProviderWebsocket_;
                $rootScope.connectSockJs = jasmine.createSpy();
                $rootScope.websocketListener = jasmine.createSpy();
            });

            listener = {
                onMetadataReceived: jasmine.createSpy(),
                onDataReceived: jasmine.createSpy()
            };

            dataProvider = new GridDataProviderWebsocket(websocketUrl, listener);
        });

        afterEach(function () {
        });

        it('connect() calls connectSockJs and websocketListener', function () {
            dataProvider.connect();

            // TODO this callback is currently called immediately because we are mocking it out.
            // TODO in the future it will only be called when the socket connection responds.
            expect(listener.onMetadataReceived).toHaveBeenCalled();
            /*
             expect(apiMock.get).toHaveBeenCalledWith({ path: 'dummy/subPath/metadata' });

             var onMetadataReceivedSuccessCallback = apiMock.success.calls.all()[0].args[0];
             onMetadataReceivedSuccessCallback('metadata');

             expect(listener.onMetadataReceived).toHaveBeenCalledWith('metadata');

             expect(apiMock.get).toHaveBeenCalledWith({ path: subPath }, gridState);

             var onDataReceivedSuccessCallback = apiMock.success.calls.all()[1].args[0];
             onDataReceivedSuccessCallback('data');

             expect(listener.onDataReceived).toHaveBeenCalledWith('data');
             */
        });

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