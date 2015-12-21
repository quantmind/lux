define(function(require) {

    describe("Test lux.grid.dataProviderFactory module", function() {

        var GridDataProviderFactory;
        var GridDataProviderRESTMock = jasmine.createSpy('GridDataProviderREST');
        var GridDataProviderWebsocketMock = jasmine.createSpy('GridDataProviderWebsocket');
        var target;
        var subPath;
        var gridState;
        var listener;

        beforeEach(function () {
            angular.mock.module('lux.grid.dataProviderFactory', function($provide) {
                $provide.value('GridDataProviderREST', GridDataProviderRESTMock);
                $provide.value('GridDataProviderWebsocket', GridDataProviderWebsocketMock);
            });

            inject(function (_GridDataProviderFactory_) {
                GridDataProviderFactory = _GridDataProviderFactory_;
            });

            target = { url: 'dummy://url'};
            targetWebsocket = { url: 'dummy://url', channel: 'dummy_channel'};
            subPath = 'dummy/subPath';
            gridState = { dummy: 'gridstate' };
            listener = { dummy: 'listener' };
        });

        afterEach(function () {
        });

        it('has a static create() method', function() {
            expect(typeof GridDataProviderFactory.create).toBe('function');
        });

        it('instantiates GridDataProviderREST by default', function() {
            GridDataProviderFactory.create();
            expect(GridDataProviderRESTMock).toHaveBeenCalled();
        });

        it('instantiates GridDataProviderREST given that connectionType and passes on other arguments', function() {
            GridDataProviderFactory.create('GridDataProviderREST', target, subPath, gridState, listener);
            expect(GridDataProviderRESTMock).toHaveBeenCalledWith(target, subPath, gridState, listener);
        });

        it('instantiates GridDataProviderWebsocket given that connectionType and passes on other arguments', function() {
            GridDataProviderFactory.create('GridDataProviderWebsocket', targetWebsocket, subPath, gridState, listener);
            expect(GridDataProviderWebsocketMock).toHaveBeenCalledWith(targetWebsocket.url, targetWebsocket.channel, listener);
        });

    });

});
