    //  Lux Api service factory for angular
    //  ---------------------------------------
    angular.module('lux.services', [])
        //
        .value('ApiTypes', {})
        //
        .service('$lux', ['$location', '$q', '$http', '$log', '$timeout', 'ApiTypes',
                function ($location, $q, $http, $log, $timeout, ApiTypes) {
            var $lux = this;

            this.location = $location;
            this.log = $log;
            this.http = $http;
            this.q = $q;
            this.timeout = $timeout;
            //  Create a client api
            //  -------------------------
            //
            //  context: an api name or an object containing, name, url and type.
            //
            //  name: the api name
            //  url: the api base url
            //  type: optional api type (default is ``lux``)
            this.api = function (url, api) {
                if (arguments.length === 1) {
                    if (isObject(url)) {
                        url = url.url;
                    }
                    api = ApiTypes[url];
                    if (!api)
                        $lux.log.error('Api client for "' + url + '" is not available');
                    else
                        return api;
                } else if (arguments.length === 2) {
                    ApiTypes[url] = api(url, this);
                    return this;
                }
            };
        }]);
    //
    function wrapPromise (promise) {
        promise.success = function(fn) {
            return wrapPromise(this.then(function(response) {
                return fn(response.data, response.status, response.headers);
            }));
        };

        promise.error = function(fn) {
            return wrapPromise(this.then(null, function(response) {
                return fn(response.data, response.status, response.headers);
            }));
        };

        return promise;
    }
    //
    //  Lux API Interface for REST
    //
    var baseapi = function (url, $lux) {
        //
        //  Object containing the urls for the api.
        var api = {},
            apiUrls;
        //
        // API base url
        api.baseUrl  = function () {
            return url;
        };

        // calculate the url for an API call
        api.httpOptions = function (request) {
            request.options.url = request.baseUrl;
        };

        // This function can be used to add authentication
        api.authentication = function (request) {};
        //
        api.get = function (opts, data) {
            return api.request('get', opts, data);
        };
        //
        // Perform the actual request and return a promise
        //      method: HTTP method
        //      urlparams:
        //      opts: object passed to
        api.request = function (method, opts, data) {
            // handle urlparams when not an object
            opts = extend({'method': method, 'data': data}, opts);

            var d = $lux.q.defer(),
                //
                request = extend({
                    name: opts.name,
                    //
                    deferred: d,
                    //
                    on: wrapPromise(d.promise),
                    //
                    options: opts,
                    //
                    error: function (data, status, headers) {
                        if (isString(data)) {
                            data = {error: true, message: data};
                        }
                        d.reject({
                            'data': data,
                            'status': status,
                            'headers': headers
                        });
                    },
                    //
                    success: function (data, status, headers) {
                        if (isString(data)) data = {message: data};

                        if (data.error)
                            d.reject({
                                'data': data,
                                'status': status,
                                'headers': headers
                            });
                        else
                            d.resolve({
                                'data': data,
                                'status': status,
                                'headers': headers
                            });
                    }
                });
            //
            delete opts.name;
            opts.method = opts.method.toLowerCase();
            if (opts.url === api.baseUrl())
                delete opts.url;
            //
            this.call(request);
            //
            return request.on;
        };
        //
        //  Execute an API call for a given request
        //  This method is hardly used directly,
        //	the ``request`` method is normally used.
        //
        //      request: a request object obtained from the ``request`` method
        api.call = function (request) {
            //
            if (!request.baseUrl && request.name) {
                if (apiUrls) {
                    request.baseUrl = apiUrls[request.name];
                    //
                    // No api url!
                    if (!request.baseUrl)
                        return request.error('Could not find a valid url for ' + request.name);

                    //
                } else {
                    // Fetch the api urls
                    $lux.log.info('Fetching api info');
                    return $lux.http.get(api.baseUrl()).success(function (resp) {
                        apiUrls = resp;
                        api.call(request);
                    }).error(request.error);
                    //
                }
            }

            if (!request.baseUrl)
                request.baseUrl = api.baseUrl();

            api.httpOptions(request);

            //
            // Fetch authentication token?
            var r = api.authentication(request);
            if (r) return r;
            //
            var options = request.options;

            if (options.url) {
                $lux.log.info('Executing HTTP ' + options.method + ' request @ ' + options.url);
                $lux.http(options).success(request.success).error(request.error);
            }
            else
                request.error('Api url not available');
        };

        return api;
    };
