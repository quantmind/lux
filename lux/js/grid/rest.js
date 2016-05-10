import _ from '../ng';


class Rest {

    constructor ($lux, grid) {
        this.grid = grid;
        this.api = $lux.api(grid.options.target);
    }

    connect () {
        return this.getMetadata();
    }

    getMetadata () {
        const grid = this.grid;
        this.api.get({
            path: 'metadata'
        }).success(function (metadata) {
            grid.$onMetadata(metadata);
        });
    }

    getData (options) {
        var grid = this.grid,
            query = grid.state.query;

        _.extend(query, options);

        return this.api.get({params: query}).success(function (data) {
            grid.$onData(data);
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
