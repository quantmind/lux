define(['angular',
        'lux/main',
        'lux/google/models'], function (angular, lux) {
    'use strict';

    lux.google.sheets = function (url, $lux) {
        url = 'https://spreadsheets.google.com';

        var api = lux.apiFactory(url, $lux);

        api.httpOptions = function (request) {
            var urlparams = request.urlparams;
            request.options.url = request.baseUrl() + '/feeds/list/' + this._url + '/' + urlparams.id + '/public/values?alt=json';
        };

        api.getList = function (options) {
            return api.request('get', null, options).then(function (response) {
                return response;
            });
        };

        api.get = function (urlparams, options) {
            var opts = this.options,
                $lux = this.$lux;
            return api.request('get', urlparams, options).then(function (response) {
                response.data = opts.orientation === 'columns' ? new lux.google.Series(
                    $lux, response.data) : new lux.google.Model($lux, response.data);
                return response;
            });
        };

        return api;
    };

    return lux;

});
