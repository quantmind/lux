import _ from '../ng';


class Rest {

    constructor ($lux, grid) {
        this.grid = grid;
        this.api = $lux.api(grid.options.target);
    }

    connect () {
        return this.getMetaData();
    }

    getMetadata () {
        const grid = this.grid,
              path = this.api.defaults.path || '';
        this.api.get({
            path: path + '/metadata'
        }).success(function (metadata) {
            grid.onMetadataReceived(metadata);
        });
    }

    getData (options) {
        var grid = this._grid,
            query = grid.state.query();

        _.extend(query, options);

        return this.api.get({params: query}).success(function (data) {
            grid.onDataReceived(data);
        });
    }

    getPage (options) {
        return this.getData(options);
    }

    deleteItem (identifier) {
        return this.api.delete({path: this._subPath + '/' + identifier});
    }
}


function rest ($lux, grid) {
    return new Rest($lux, grid);
}


rest.prototype = Rest.prototype;


export default rest;
