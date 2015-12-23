//  Grid Data Provider Factory
//	===================
//
//	Selects appropriate grid data provider class depending on connection type
define(['angular',
        'lux/grid/data-providers/rest',
        'lux/grid/data-providers/websocket'], function (angular) {

    angular.module('luxGridDataProvider', [
            'luxGridDataProviderRest',
            'luxGridDataProviderWebsocket'
        ])
        .factory('GridDataProviderFactory', [
            'GridDataProviderREST',
            'GridDataProviderWebsocket',
            gridDataProviderFactoryFactory]);

    function gridDataProviderFactoryFactory(GridDataProviderREST, GridDataProviderWebsocket) {

        function create(connectionType, target, subPath, gridState, listener) {
            switch (connectionType) {
                case 'GridDataProviderREST':
                    return new GridDataProviderREST(target, subPath, gridState, listener);
                case 'GridDataProviderWebsocket':
                    return new GridDataProviderWebsocket(target.url, target.channel, listener);
                default:
                    return new GridDataProviderREST(target, subPath, gridState, listener);
            }
        }

        return {create: create};
    }

});
