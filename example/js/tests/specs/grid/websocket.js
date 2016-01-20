define(['tests/mocks/lux',
        'lux',
        'lux/grid',
        'lux/grid/websocket'], function () {
    'use strict';

    describe('Test lux.grid.dataProviderWebsocket module', function() {

        var GridDataProviderWebsocket;
        var listener;
        var dataProvider;
        var websocketUrl = 'websocket://url';
        var channel = 'some channel';
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

            angular.mock.module('lux.grid.websocket', function ($provide) {
                $provide.value('$lux', {});
            });

            listener = {
                onMetadataReceived: jasmine.createSpy(),
                onDataReceived: jasmine.createSpy()
            };

            dataProvider = new GridDataProviderWebsocket(websocketUrl, channel, listener);
        });

        it('connect()', function () {
            dataProvider.connect();

            expect(sockJsSpy).toHaveBeenCalledWith(websocketUrl);
            expect(addListenerSpy).toHaveBeenCalledWith(channel, jasmine.any(Function));
            expect(connectSpy).toHaveBeenCalledWith(jasmine.any(Function));
        });

        it('connect() passes record-update data from websocket response to onDataReceived', function () {
            var msg = {
                data: {
                    event: 'record-update',
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
                data: {
                    event: 'records',
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
                data: {
                    event: 'columns-metadata',
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
});
