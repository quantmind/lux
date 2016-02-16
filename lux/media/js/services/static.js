define(['angular', 'lux/main'], function (angular, lux) {
    'use strict';

    var pageCache = {};
    //
    //  Lux Static site JSON API
    //  ------------------------
    //
    //  Api used by static sites
    angular.module('lux.static.api', ['lux.services'])

        .run(['$rootscope', '$lux', '$window', function (scope, $lux, $window) {

            if (scope.API_URL)
                $lux.api(scope.API_URL, luxstatic);

            function luxstatic(url, $lux) {

                var api = lux.apiFactory(url, $lux);

                api.url = function (urlparams) {
                    var url = this._url,
                        name = urlparams ? urlparams.slug : null;
                    if (url.substring(url.length - 5) === '.json')
                        return url;
                    if (url.substring(url.length - 1) !== '/')
                        url += '/';
                    url += name || 'index';
                    if (url.substring(url.length - 5) === '.html')
                        url = url.substring(0, url.length - 5);
                    else if (url.substring(url.length - 1) === '/')
                        url += 'index';
                    if (url.substring(url.length - 5) !== '.json')
                        url += '.json';
                    return url;
                };

                api.getPage = function (page, state, stateParams) {
                    var href = lux.stateHref(state, page.name, stateParams),
                        data = pageCache[href];
                    if (data)
                        return data;
                    //
                    return this.get(stateParams).then(function (response) {
                        var data = response.data;
                        pageCache[href] = data;
                        lux.forEach(data.require_css, function (css) {
                            lux.loadCss(css);
                        });
                        if (data.require_js) {
                            var defer = $lux.q.defer();
                            require(data.require_js, function () {
                                // let angular resolve its queue if it needs to
                                defer.resolve(data);
                            });
                            return defer.promise;
                        } else
                            return data;
                    }, function (response) {
                        if (response.status === 404) {
                            $window.location.reload();
                        }
                    });
                };

                api.getItems = function (page) {
                    if (page.apiItems)
                        return this.getList({url: this._url + '.json'});
                };

                return api;
            }

        }]);

});
