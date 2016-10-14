import _ from '../ng';


class Rest {

    constructor (grid) {
        this.grid = grid;
        this.api = grid.$lux.api(grid.options.target);
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
        return this.api.delete({url: identifier});
    }
}


function rest (grid) {
    return new Rest(grid);
}


rest.prototype = Rest.prototype;


export default rest;
