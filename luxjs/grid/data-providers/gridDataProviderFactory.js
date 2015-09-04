//  Grid Data Provider Factory
//	===================
//
//	Selects appropriate grid data provider class depending on connection type

angular.module('lux.grid.dataProviderFactory', [
    'lux.grid.dataProviderREST',
    'lux.grid.dataProviderWebsocket'
])
    .factory('GridDataProviderFactory', [
        'GridDataProviderREST',
        'GridDataProviderWebsocket',
        gridDataProviderFactoryFactory]);

function gridDataProviderFactoryFactory (GridDataProviderREST, GridDataProviderWebsocket) {

    function create(connectionType, target, subPath, gridState, listener) {
        switch (connectionType) {
            case 'GridDataProviderREST':
                return new GridDataProviderREST(target, subPath, gridState, listener);
            case 'GridDataProviderWebsocket':
                return new GridDataProviderWebsocket(target.url + '/stream', listener);
            default:
                return new GridDataProviderREST(target, subPath, gridState, listener);
        }
    }

    return { create: create };
}
