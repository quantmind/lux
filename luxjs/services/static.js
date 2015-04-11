    //
    //  Lux Static site JSON API
    //  ------------------------
    //
    //  Api used by static sites
    angular.module('lux.static.api', ['lux.services'])

        .run(['$lux', '$window', function ($lux, $window) {
            var pageCache = {};

            $lux.$window = $window;
            //
            if (scope.API_URL)
                $lux.api(scope.API_URL, luxstatic);
        }]);


    var luxstatic = function (url, $lux) {

        var api = baseapi(url, $lux);

        api.url = function (urlparams) {
            var url = this._url,
                name = urlparams ? urlparams.slug : null;
            if (url.substring(url.length-5) === '.json')
                return url;
            if (url.substring(url.length-1) !== '/')
                url += '/';
            url += name || 'index';
            if (url.substring(url.length-5) === '.html')
                url = url.substring(0, url.length-5);
            else if (url.substring(url.length-1) === '/')
                url += 'index';
            if (url.substring(url.length-5) !== '.json')
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
                forEach(data.require_css, function (css) {
                    loadCss(css);
                });
                if (data.require_js) {
                    var defer = $lux.q.defer();
                    require(rcfg.min(data.require_js), function () {
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

        api.getItems = function (page, state, stateParams) {
            if (page.apiItems)
                return this.getList({url: this._url + '.json'});
        };

        return api;
    };

