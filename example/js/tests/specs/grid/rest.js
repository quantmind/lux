define(['tests/mocks/lux',
        'lux/grid',
        'lux/grid/rest'], function () {
    'use strict';

    describe('Test lux.grid.rest module', function() {

        var GridDataProviderREST;
        var apiMock;
        var listener;
        var dataProvider;
        var target = { url: 'dummy://url'};
        var subPath = 'dummy/subPath';
        var gridState = { dummy: 'gridstate' };
        var options = { dummy: 'options' };

        beforeEach(function () {

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

        it('connect()', function() {
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

        it('getPage()', function() {
            dataProvider.getPage(options);

            expect(apiMock.get).toHaveBeenCalledWith({}, options);

            var onDataReceivedSuccessCallback = apiMock.success.calls.all()[0].args[0];
            onDataReceivedSuccessCallback('data');

            expect(listener.onDataReceived).toHaveBeenCalledWith('data');
        });

        it('deleteItem()', function() {
            var identifier = 'my ID';
            var onSuccess = function() {};
            var onFailure = function() {};

            dataProvider.deleteItem(identifier, onSuccess, onFailure);

            expect(apiMock.delete).toHaveBeenCalledWith({ path: subPath + '/' + identifier});
            expect(apiMock.success).toHaveBeenCalledWith(onSuccess);
            expect(apiMock.error).toHaveBeenCalledWith(onFailure);
        });

        it('destroy()', function() {
            dataProvider.destroy();

            expect(dataProvider.connect).toThrow();
        });

    });

});
