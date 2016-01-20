define(function(require) {

    describe("Test lux.grid.dataProviderWebsocket module", function() {

        var GridDataProviderWebsocket;
        var listener;
        var dataProvider;
        var websocketUrl = 'websocket://url';
        var channel = 'some channel';
        var scope = {};
        var connectSpy;
        var addListenerSpy;
        var sockJsSpy;

        beforeEach(function () {
            sockJsSpy = jasmine.createSpy();
            connectSpy = jasmine.createSpy();
            addListenerSpy = jasmine.createSpy();

            sockJsSpy.and.returnValue({
                connect: connectSpy,
                addListener: addListenerSpy
            });

            angular.mock.module('lux.grid.dataProviderWebsocket', function ($provide) {
                $provide.value('$lux', {});
            });

            inject(function (_GridDataProviderWebsocket_, $rootScope) {
                GridDataProviderWebsocket = _GridDataProviderWebsocket_;
                $rootScope.sockJs = sockJsSpy;
            });

            listener = {
                onMetadataReceived: jasmine.createSpy(),
                onDataReceived: jasmine.createSpy()
            };

            dataProvider = new GridDataProviderWebsocket(websocketUrl, channel, listener);
        });

        afterEach(function () {
        });

        it('connect() calls connectSockJs and websocketListener', function () {
            dataProvider.connect();

            expect(sockJsSpy).toHaveBeenCalledWith(websocketUrl);
            expect(addListenerSpy).toHaveBeenCalledWith(channel, jasmine.any(Function));
            expect(connectSpy).toHaveBeenCalledWith(jasmine.any(Function));
        });

        it('connect() passes record-update data from websocket response to onDataReceived', function () {
            var msg = {
                event: 'record-update',
                data: {
                    data: 'dummy data'
                }
            };

            dataProvider.connect();

            var onMessage = addListenerSpy.calls.all()[0].args[1];

            onMessage({}, msg);

            expect(listener.onDataReceived).toHaveBeenCalledWith(jasmine.any(Object));
            var obj = listener.onDataReceived.calls.all()[0].args[0];
            expect(obj.result).toBe('dummy data');

        });

        it('connect() passes records data from websocket response to onDataReceived', function () {
            var msg = {
                event: 'records',
                data: {
                    data: 'dummy data'
                }
            };

            dataProvider.connect();

            var onMessage = addListenerSpy.calls.all()[0].args[1];

            onMessage({}, msg);

            expect(listener.onDataReceived).toHaveBeenCalledWith(jasmine.any(Object));
            var obj = listener.onDataReceived.calls.all()[0].args[0];
            expect(obj.result).toBe('dummy data');

        });

        it('connect() passes columns-metadata data from websocket response to onMetadataReceived', function () {
            var msg = {
                event: 'columns-metadata',
                data: {
                    data: 'dummy data'
                }
            };

            dataProvider.connect();

            var onMessage = addListenerSpy.calls.all()[0].args[1];

            onMessage({}, msg);

            expect(listener.onMetadataReceived).toHaveBeenCalledWith('dummy data');
        });

        it('destroy() disables the data provider', function () {
            dataProvider.destroy();

            expect(dataProvider.connect).toThrow();
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