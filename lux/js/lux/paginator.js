
class Paginator {

    constructor (api) {
        this.api = api;
    }

    getData (opts, callback) {
        this.api.get(opts).then(function (response) {
            callback(response.data);
        });
    }

}


export default function paginator (api) {
    return new Paginator(api);
}


paginator.prototype = Paginator.prototype;
