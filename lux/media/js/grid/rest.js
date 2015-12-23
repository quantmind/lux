//  Grid Data Provider
//	===================
//
//	provides data to a lux.grid using REST calls
define(['angular', 'lux.grid'], function (angular, lux) {
    "use strict";

    angular.module('lux.grid.rest', ['lux.grid'])

        .run(['$lux', 'luxGridDataProviders'], function ($lux, luxGridDataProviders) {

            luxGridDataProviders.register('rest', restProvider($lux));
        });

    function restProvider ($lux) {

        function GridDataProviderREST(target, subPath, gridState, listener) {
            this._api = $lux.api(target);
            this._subPath = subPath;
            this._gridState = gridState;
            this._listener = listener;
        }

        GridDataProviderREST.prototype.connect = function () {
            checkIfDestroyed.call(this);
            getMetadata.call(this, getData.bind(this, {path: this._subPath}, this._gridState));
        };

        GridDataProviderREST.prototype.getPage = function (options) {
            checkIfDestroyed.call(this);
            getData.call(this, {}, options);
        };

        GridDataProviderREST.prototype.deleteItem = function (identifier, onSuccess, onFailure) {
            checkIfDestroyed.call(this);
            this._api.delete({path: this._subPath + '/' + identifier})
                .success(onSuccess)
                .error(onFailure);
        };

        GridDataProviderREST.prototype.destroy = function () {
            this._listener = null;
        };

        function checkIfDestroyed() {
            /* jshint validthis:true */
            if (this._listener === null || typeof this._listener === 'undefined') {
                throw 'GridDataProviderREST#connect error: either you forgot to define a listener, or you are attempting to use this data provider after it was destroyed.';
            }
        }

        function getMetadata(callback) {
            /* jshint validthis:true */
            this._api.get({
                path: this._subPath + '/metadata'
            }).success(function (metadata) {
                this._listener.onMetadataReceived(metadata);
                if (typeof callback === 'function') {
                    callback();
                }
            }.bind(this));
        }

        function getData(path, options) {
            /* jshint validthis:true */
            this._api.get(path, options).success(function (data) {
                this._listener.onDataReceived(data);
            }.bind(this));
        }

        return GridDataProviderREST;
    }

});
