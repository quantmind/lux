//  Grid Data Provider
//	===================
//
//	provides data to a lux.grid using REST calls

angular.module('lux.grid.dataProviderREST', ['lux.services'])
    .factory('GridDataProviderREST', ['$lux', gridDataProviderRESTFactory]);

function gridDataProviderRESTFactory ($lux) {

    function GridDataProviderREST(target, subPath, gridState, listener) {
        this._api = $lux.api(target);
        this._subPath = subPath;
        this._gridState = gridState;
        this._listener = listener;
    }

    GridDataProviderREST.prototype.destroy = function() {
        this._listener = null;
    };

    GridDataProviderREST.prototype.connect = function() {
        getMetadata.call(this, getData.bind(this, { path: this._subPath }, this._gridState));
    };

    GridDataProviderREST.prototype.getPage = function(options) {
        getData.call(this, {}, options);
    };

    GridDataProviderREST.prototype.deleteItem = function(identifier, onSuccess, onFailure) {
        this._api.delete({path: this._subPath + '/' + identifier})
            .success(onSuccess)
            .error(onFailure);
    };

    function getMetadata(callback) {
        /* jshint validthis:true */
        this._api.get({
            path: this._subPath + '/metadata'
        }).success(function(metadata) {
            this._listener.onMetadataReceived(metadata);
            if (typeof callback === 'function') {
                callback();
            }
        }.bind(this));
    }

    function getData(path, options) {
        /* jshint validthis:true */
        this._api.get(path, options).success(function(data) {
            this._listener.onDataReceived(data);
        }.bind(this));
    }

    return GridDataProviderREST;
}
