import _ from '../ng';


class Paginator {

    constructor (api) {
        this.api = api;
    }

    getData (opts, callback) {
        if (arguments.length === 1 && _.isFunction(opts)) {
            callback = opts;
            opts = null;
        }
        this.api.get(opts).then(function (response) {
            var data = response.data;
            if (callback)
                callback(data.result);
        });
    }

}


export default function paginator (api) {
    return new Paginator(api);
}


paginator.prototype = Paginator.prototype;
