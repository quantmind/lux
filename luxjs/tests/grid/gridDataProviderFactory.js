define(function(require) {

    describe("Test lux.grid.dataProviderFactory module", function() {

        var GridDataProviderFactory;
        var GridDataProviderRESTMock = jasmine.createSpy('GridDataProviderREST');
        var GridDataProviderWebsocketMock = jasmine.createSpy('GridDataProviderWebsocket');

        beforeEach(function () {
            angular.mock.module('lux.grid.dataProviderFactory', function($provide) {
                $provide.value('GridDataProviderREST', GridDataProviderRESTMock);
                $provide.value('GridDataProviderWebsocket', GridDataProviderWebsocketMock);
            });

            inject(function (_GridDataProviderFactory_) {
                GridDataProviderFactory = _GridDataProviderFactory_;
            });
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
            var target = { url: 'dummy://url'};
            var subPath = 'dummy/subPath';
            var gridState = { dummy: 'gridstate' };
            var listener = { dummy: 'listener' };

            GridDataProviderFactory.create('GridDataProviderREST', target, subPath, gridState, listener);
            expect(GridDataProviderRESTMock).toHaveBeenCalledWith(target, subPath, gridState, listener);
        });

        it('instantiates GridDataProviderWebsocket given that connectionType and passes on other arguments', function() {
            var target = { url: 'dummy://url'};
            var subPath = 'dummy/subPath';
            var gridState = { dummy: 'gridstate' };
            var listener = { dummy: 'listener' };

            GridDataProviderFactory.create('GridDataProviderWebsocket', target, subPath, gridState, listener);
            expect(GridDataProviderWebsocketMock).toHaveBeenCalledWith('dummy://url/stream', listener);
        });

    });

});
