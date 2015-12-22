define(['angular',
        'lux',
        'lux/google/sheets',
        'lux/services/api'], function (angular, lux, google, apiFactory) {

    google.sheets = function (url, $lux) {
        url = "https://spreadsheets.google.com";

        var api = apiFactory(url, $lux);

        api.httpOptions = function (request) {
            request.options.url = request.baseUrl() + '/feeds/list/' + this._url + '/' + urlparams.id + '/public/values?alt=json';
        };

        api.getList = function (options) {
            var Model = this.Model,
                opts = this.options,
                $lux = this.$lux;
            return api.request('get', null, options).then(function (response) {
                return response;
            });
        };

        api.get = function (urlparams, options) {
            var Model = this.Model,
                opts = this.options,
                $lux = this.$lux;
            return api.request('get', urlparams, options).then(function (response) {
                response.data = opts.orientation === 'columns' ? new GoogleSeries(
                    $lux, response.data) : new GoogleModel($lux, response.data);
                return response;
            });
        };

        return api;
    };

    return google;

});
