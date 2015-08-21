//  Grid Data Provider Factory
//	===================
//
//	Selects appropriate grid data provider class depending on connection type

angular.module('lux.gridDataProviderFactory', [
    'lux.gridDataProviderREST',
    'lux.gridDataProviderWebsocket'
])
    .factory('GridDataProviderFactory', [
        'GridDataProviderREST',
        'GridDataProviderWebsocket',
        gridDataProviderFactoryFactory]);

function gridDataProviderFactoryFactory (GridDataProviderREST, GridDataProviderWebsocket) {

    function create(connectionType, target, subPath, gridState) {
        switch (connectionType) {
            case 'GridDataProviderREST':
                return new GridDataProviderREST(target, subPath, gridState);
            case 'GridDataProviderWebsocket':
                return new GridDataProviderWebsocket(target.url + '/stream', gridState);
            default:
                return new GridDataProviderREST(target, subPath, gridState);
        }
    }

    return { create: create };
}
