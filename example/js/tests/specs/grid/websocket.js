define(['angular',
        'lux',
        'lux/grid/websocket'], function (angular) {
    'use strict';

    describe('Test lux.grid.dataProviderWebsocket module', function() {

        var luxGridDataProviders;

        angular.module('lux.grid.websocket.test', ['lux.loader',
            'lux.mocks.http', 'lux.grid.websocket'])
            .value('context', {API_URL: '/api'});

        beforeEach(function () {
            module('lux.grid.websocket.test');

            inject(function (_luxGridDataProviders_) {
                luxGridDataProviders = _luxGridDataProviders_;
            });
        });

        it('websocket provider', function () {
            var websocket = luxGridDataProviders.create({options: {dataProvider: 'websocket'}});
            expect(angular.isObject(websocket._grid)).toBe(true);
            expect(websocket._grid.options.dataProvider).toBe('websocket');
        });

    });
});
