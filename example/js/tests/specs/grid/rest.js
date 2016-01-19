define(['angular',
        'tests/mocks/lux',
        'lux/grid',
        'lux/grid/rest'], function (angular) {
    'use strict';

    describe('Test lux.grid.rest module', function() {

        var $lux = angular.injector(['lux.mocks.lux']).get('$lux');
        var api = $lux.api();
        var GridDataProviderREST;
        var listener;
        var dataProvider;
        var target = { url: 'dummy://url'};
        var subPath = 'dummy/subPath';
        var gridState = { dummy: 'gridstate' };
        var options = { dummy: 'options' };

        beforeEach(function () {

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

            expect(api.get).toHaveBeenCalledWith({ path: 'dummy/subPath/metadata' });

            var onMetadataReceivedSuccessCallback = api.success.calls.all()[0].args[0];
            onMetadataReceivedSuccessCallback('metadata');

            expect(listener.onMetadataReceived).toHaveBeenCalledWith('metadata');

            expect(api.get).toHaveBeenCalledWith({ path: subPath }, gridState);

            var onDataReceivedSuccessCallback = api.success.calls.all()[1].args[0];
            onDataReceivedSuccessCallback('data');

            expect(listener.onDataReceived).toHaveBeenCalledWith('data');

        });

        it('getPage()', function() {
            dataProvider.getPage(options);

            expect(api.get).toHaveBeenCalledWith({}, options);

            var onDataReceivedSuccessCallback = api.success.calls.all()[0].args[0];
            onDataReceivedSuccessCallback('data');

            expect(listener.onDataReceived).toHaveBeenCalledWith('data');
        });

        it('deleteItem()', function() {
            var identifier = 'my ID';
            var onSuccess = function() {};
            var onFailure = function() {};

            dataProvider.deleteItem(identifier, onSuccess, onFailure);

            expect(api.delete).toHaveBeenCalledWith({ path: subPath + '/' + identifier});
            expect(api.success).toHaveBeenCalledWith(onSuccess);
            expect(api.error).toHaveBeenCalledWith(onFailure);
        });

        it('destroy()', function() {
            dataProvider.destroy();

            expect(dataProvider.connect).toThrow();
        });

    });

});
