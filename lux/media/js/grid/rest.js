//  Grid REST Data Provider
//	==========================
//
//	provides data to a lux.grid using REST calls
define(['angular',
        'lux/grid'], function (angular) {
    'use strict';

    angular.module('lux.grid.rest', ['lux.grid'])

        .run(['$lux', 'luxGridDataProviders', function ($lux, luxGridDataProviders) {

            luxGridDataProviders.register('rest', restProvider($lux, luxGridDataProviders));
        }]);

    function restProvider ($lux, dataProvider) {

        function GridDataProviderREST (grid) {
            var target = grid.options.target;
            this._api = $lux.api(target);
            this._grid = grid;
        }

        GridDataProviderREST.prototype.connect = function () {
            dataProvider.check(this);
            getMetadata(this);
        };

        GridDataProviderREST.prototype.getPage = function (options) {
            dataProvider.check(this);
            getData(this, {}, options);
        };

        GridDataProviderREST.prototype.deleteItem = function (identifier, onSuccess, onFailure) {
            dataProvider.check(this);
            this._api.delete({path: this._subPath + '/' + identifier})
                .success(onSuccess)
                .error(onFailure);
        };

        GridDataProviderREST.prototype.destroy = function () {
            this._gridApi = null;
        };

        return GridDataProviderREST;

        function getMetadata(self) {
            self._api.get({
                path: 'metadata'
            }).success(function (metadata) {
                self._gridApi.lux.onMetadataReceived(metadata);
            });
        }

        function getData(self) {
            var grid = self._gridApi.lux,
                query = grid.state.query();
            self._api.get({params: query}).success(function (data) {
                grid.onDataReceived(data);
            });
        }
    }

});
