define(function(require) {

    describe("Test lux.grid.dataProviderWebsocket module", function() {

        var GridDataProviderWebsocket;
        var listener;
        var dataProvider;
        var websocketUrl = 'websocket://url';
        var scope = {};
        var connectSockJsSpy;
        var websocketListenerSpy;

        beforeEach(function () {
            connectSockJsSpy = jasmine.createSpy();
            websocketListenerSpy = jasmine.createSpy();

            angular.mock.module('lux.grid.dataProviderWebsocket', function ($provide) {
                $provide.value('$lux', {});
            });

            inject(function (_GridDataProviderWebsocket_, $rootScope) {
                GridDataProviderWebsocket = _GridDataProviderWebsocket_;
                $rootScope.connectSockJs = connectSockJsSpy;
                $rootScope.websocketListener = websocketListenerSpy;
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

            expect(connectSockJsSpy).toHaveBeenCalledWith(websocketUrl);
            expect(websocketListenerSpy).toHaveBeenCalledWith('bmll_celery', jasmine.any(Function));
        });

        it('connect() passes data from websocket response to onDataReceived', function () {
            dataProvider.connect();

            var callback = websocketListenerSpy.calls.all()[0].args[1];

            callback({}, {
                data: {
                    event: 'task-status',
                    data: 'dummy data'
                }
            });

            expect(listener.onDataReceived).toHaveBeenCalled();
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