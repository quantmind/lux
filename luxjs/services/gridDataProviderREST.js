//  Grid Data Provider
//	===================
//
//	provides data to a lux.grid using REST calls

angular.module('lux.gridDataProviderREST', ['lux.services'])
    .factory('GridDataProviderREST', ['$lux', gridDataProviderRESTFactory]);

function gridDataProviderRESTFactory ($lux) {

    function GridDataProviderREST(target, subPath, gridState) {
        this.api = $lux.api(target);
        this.subPath = subPath;
        this.gridState = gridState;

        this.listeners = [];
    }

    GridDataProviderREST.prototype.addListener = function(listener) {
        this.listeners.push(listener);
    };

    GridDataProviderREST.prototype.removeListener = function(listener) {
        var index = this.listeners.indexOf(listener);
        if (index !== -1) {
            this.listeners.splice(index, 1);
        }
    };

    GridDataProviderREST.prototype.removeListeners = function() {
        this.listeners = [];
    };

    GridDataProviderREST.prototype.connect = function() {
        getMetadata.call(this, getData.bind(this, { path: this.subPath }, this.gridState));
    };

    GridDataProviderREST.prototype.getPage = function(options) {
        getData.call(this, {}, options);
    };

    GridDataProviderREST.prototype.deleteItem = function(identifier, onSuccess, onFailure) {
        this.api.delete({path: this.subPath + '/' + identifier})
            .success(onSuccess)
            .error(onFailure);
    };

    function getMetadata(callback) {
        /* jshint validthis:true */
        this.api.get({
            path: this.subPath + '/metadata'
        }).success(function(metadata) {
            this.listeners.forEach(function(listener) {
                listener.onMetadataReceived(metadata);
            });
            if (typeof callback === 'function') {
                callback();
            }
        }.bind(this));
    }

    function getData(path, options) {
        /* jshint validthis:true */
        this.api.get(path, options).success(function(data) {
            this.listeners.forEach(function(listener) {
                listener.onDataReceived(data);
            });
        }.bind(this));
    }

    return GridDataProviderREST;
}
