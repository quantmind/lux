    //  Lux Api service factory for angular
    //  ---------------------------------------
    angular.module('lux.services', [])
        //
        .value('ApiTypes', {})
        //
        .run(['$rootScope', '$lux', function (scope, $lux) {
            //
            //  Listen for a Lux form to be available
            //  If it uses the api for posting, register with it
            scope.$on('formReady', function (e, model, formScope) {
                var attrs = formScope.formAttrs,
                    action = attrs ? attrs.action : null;
                if (isObject(action)) {
                    var api = $lux.api(action);
                    if (api) {
                        $lux.log.info('Form ' + formScope.formModelName + ' registered with "' +
                            api.toString() + '" api');
                        api.formReady(model, formScope);
                    }
                }
            });
        }])
        //
        .service('$lux', ['$location', '$window', '$q', '$http', '$log', '$timeout', 'ApiTypes',
                function ($location, $window, $q, $http, $log, $timeout, ApiTypes) {
            var $lux = this;

            this.location = $location;
            this.window = $window;
            this.log = $log;
            this.http = $http;
            this.q = $q;
            this.timeout = $timeout;
            this.apiUrls = {};
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
                    var defaults;
                    if (isObject(url)) {
                        defaults = url;
                        url = url.url;
                    }
                    api = ApiTypes[url];
                    if (!api)
                        $lux.log.error('Api client for "' + url + '" is not available');
                    else
                        return api(url, this).defaults(defaults);
                } else if (arguments.length === 2) {
                    ApiTypes[url] = api;
                    return this;
                }
            };
        }]);
    //
    function wrapPromise (promise) {

        promise.success = function(fn) {

            return wrapPromise(this.then(function(response) {
                var r = fn(response.data, response.status, response.headers);
                return r === undefined ? response : r;
            }));
        };

        promise.error = function(fn) {

            return wrapPromise(this.then(null, function(response) {
                var r = fn(response.data, response.status, response.headers);
                return r === undefined ? response : r;
            }));
        };

        return promise;
    }

    var ENCODE_URL_METHODS = ['delete', 'get', 'head', 'options'];
    //
    //  Lux API Interface for REST
    //
    var baseapi = function (url, $lux) {
        //
        //  Object containing the urls for the api.
        var api = {},
            defaults = {};

        api.toString = function () {
            if (defaults && defaults.name)
                return api.baseUrl() + '/' + defaults.name;
            else
                return api.baseUrl();
        };
        //
        // Get/Set defaults options for requests
        api.defaults = function (_) {
            if (!arguments.length) return defaults;
            if (_)
                defaults = _;
            return api;
        };

        api.formReady = function (model, formScope) {
            $ux.log.error('Cannot handle form ready');
        };
        //
        // API base url
        api.baseUrl  = function () {
            return url;
        };

        // calculate the url for an API call
        api.httpOptions = function (request) {};

        // This function can be used to add authentication
        api.authentication = function (request) {};
        //
        api.get = function (opts, data) {
            return api.request('get', opts, data);
        };
        //
        api.post = function (opts, data) {
            return api.request('post', opts, data);
        };

        //
        // Perform the actual request and return a promise
        //	method: HTTP method
        //  opts: request options to override defaults
        //	data: body or url data
        api.request = function (method, opts, data) {
            // handle urlparams when not an object
            var o = extend({}, api.defaults());
            o.method = method.toLowerCase();
            if (ENCODE_URL_METHODS.indexOf(o.method) === -1) o.data = data;
            else o.params = data;

            opts = extend(o, opts);

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
                    error: function (respose) {
                        if (isString(respose.data))
                            respose.data = {error: true, message: data};
                        d.reject(respose);
                    },
                    //
                    success: function (response) {
                        if (isString(response.data))
                            respose.data = {message: data};

                        if (!response.data || response.data.error)
                            d.reject(response);
                        else
                            d.resolve(response);
                    }
                });
            //
            delete opts.name;
            if (opts.url === api.baseUrl())
                delete opts.url;
            //
            api.call(request);
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
                var apiUrls = $lux.apiUrls[url];

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
                    return $lux.http.get(api.baseUrl()).then(function (resp) {
                        $lux.apiUrls[url] = resp.data;
                        api.call(request);
                    }, request.error);
                    //
                }
            }

            if (!request.baseUrl)
                request.baseUrl = api.baseUrl();

            var opts = request.options;

            if (!opts.url) {
                var href = request.baseUrl;
                if (opts.path)
                    href = request.baseUrl + opts.path;
                opts.url = href;
            }

            api.httpOptions(request);

            //
            // Fetch authentication token?
            var r = api.authentication(request);
            if (r) return r;
            //
            var options = request.options;

            if (options.url) {
                $lux.log.info('Executing HTTP ' + options.method + ' request @ ' + options.url);
                $lux.http(options).then(request.success, request.error);
            }
            else
                request.error('Api url not available');
        };

        return api;
    };
