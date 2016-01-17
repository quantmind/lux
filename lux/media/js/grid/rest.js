//  Grid Data Provider
//	===================
//
//	provides data to a lux.grid using REST calls
define(['angular', 'lux/grid'], function (angular) {
    'use strict';

    angular.module('lux.grid.rest', ['lux.grid'])

        .run(['$lux', 'luxGridDataProviders'], function ($lux, luxGridDataProviders) {

            luxGridDataProviders.register('rest', restProvider($lux, luxGridDataProviders));
        });

    function restProvider ($lux, dataProvider) {

        function GridDataProviderREST (target, subPath, gridState, listener) {
            this._api = $lux.api(target);
            this._subPath = subPath;
            this._gridState = gridState;
            this._listener = listener;
        }

        GridDataProviderREST.prototype.connect = function () {
            dataProvider.check(this);
            getMetadata(this, getData.bind(this, {path: this._subPath}, this._gridState));
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
            this._listener = null;
        };

        function getMetadata(self, callback) {
            self._api.get({
                path: self._subPath + '/metadata'
            }).success(function (metadata) {
                self._listener.onMetadataReceived(metadata);
                if (angular.isFunction(callback)) callback();
            });
        }

        function getData(self, path, options) {
            self._api.get(path, options).success(function (data) {
                self._listener.onDataReceived(data);
            });
        }

        return GridDataProviderREST;
    }

});
