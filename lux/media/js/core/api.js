define(['angular',
        'lux/config/main'], function (angular, lux) {
    'use strict';

    var extend = angular.extend;

    lux.messages.no_api = function (url) {
        return {
            text: 'Api client for "' + url + '" is not available',
            icon: 'fa fa-exclamation-triangle'
        };
    };

    //  Lux Api service
    //	===================
    //
    //	A factory of javascript clients to web services
    angular.module('lux.services', [])
        //
        .constant('loginUrl', lux.context.LOGIN_URL || '')
        //
        .constant('postLoginUrl', lux.context.POST_LOGIN_URL || '/')
        // Registered api
        .value('ApiTypes', {})
        //
        .value('AuthApis', {})
        //
        .run(['$window', '$lux', function ($window, $lux) {
            //
            var doc = $window.document,
                name = angular.element(doc.querySelector('meta[name=csrf-param]')).attr('content'),
                csrf_token = angular.element(doc.querySelector('meta[name=csrf-token]')).attr('content');

            $lux.user_token = angular.element(doc.querySelector('meta[name=user-token]')).attr('content');

            if (name && csrf_token) {
                $lux.csrf = {};
                $lux.csrf[name] = csrf_token;
            }
        }])
        //
        .factory('luxHttpPromise', [function () {
            //
            return _luxHttpPromise();
        }])
        //
        .factory('$lux', ['$location', '$window', '$q', '$http', '$log',
            '$timeout', 'ApiTypes', 'AuthApis', '$templateCache', '$compile',
            '$rootScope', 'luxHttpPromise',
            function ($location, $window, $q, $http, $log, $timeout,
                      ApiTypes, AuthApis, $templateCache, $compile,
                      $scope, luxHttpPromise) {

                var $lux = {
                    location: $location,
                    window: $window,
                    log: $log,
                    http: $http,
                    q: $q,
                    timeout: $timeout,
                    templateCache: $templateCache,
                    compile: $compile,
                    apiUrls: {},
                    promise: luxHttpPromise,
                    api: api,
                    authApi: authApi,
                    formData: formData,
                    renderTemplate: renderTemplate,
                    messages: extend({}, lux.messageService, {
                        pushMessage: function (message) {
                            this.log($log, message);
                            $scope.$broadcast('messageAdded', message);
                        }
                    })
                };
                return $lux;
                //  Create a client api
                //  -------------------------
                //
                //  context: an api name or an object containing, name, url and type.
                //
                //  name: the api name
                //  url: the api base url
                //  type: optional api type (default is ``lux``)
                function api (url, api) {
                    if (arguments.length === 1) {
                        var defaults;
                        if (angular.isObject(url)) {
                            defaults = url;
                            url = url.url;
                        }
                        api = ApiTypes[url];
                        if (!api)
                            $lux.messages.error(lux.messages.no_api(url));
                        else
                            return api(url, this).defaults(defaults);
                    } else if (arguments.length === 2) {
                        ApiTypes[url] = api;
                        return api(url, this);
                    }
                }

                //
                // Set/get the authentication handler for a given api
                function authApi (api, auth) {
                    if (arguments.length === 1)
                        return AuthApis[api.baseUrl()];
                    else if (arguments.length === 2)
                        AuthApis[api.baseUrl()] = auth;
                }

                //
                // Change the form data depending on content type
                function formData (contentType) {

                    return function (data) {
                        data = extend(data || {}, $lux.csrf);
                        if (contentType === 'application/x-www-form-urlencoded')
                            return angular.element.param(data);
                        else if (contentType === 'multipart/form-data') {
                            var fd = new FormData();
                            angular.forEach(data, function (value, key) {
                                fd.append(key, value);
                            });
                            return fd;
                        } else {
                            return angular.toJson(data);
                        }
                    };
                }
                //
                // Render a template from a url
                function renderTemplate (url, element, scope, callback) {
                    var template = $templateCache.get(url);
                    if (!template) {
                        $http.get(url).then(function (resp) {
                            template = resp.data;
                            $templateCache.put(url, template);
                            _render(element, template, scope, callback);
                        }, function () {
                            $lux.messages.error('Could not load template from ' + url);
                        });
                    } else
                        _render(element, template, scope, callback);
                }

                function _render(element, template, scope, callback) {
                    var elem = $compile(template)(scope);
                    element.append(elem);
                    if (callback) callback(elem);
                }
            }]);

    var ENCODE_URL_METHODS = ['delete', 'get', 'head', 'options'];
    //
    //  Lux API Interface for REST
    //
    lux.apiFactory = function (url, $lux) {
        //
        //  Object containing the urls for the api.
        var api = {},
            defaults = {};

        api.toString = function () {
            if (defaults.name)
                return lux.joinUrl(api.baseUrl(), defaults.name);
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

        api.formReady = function () {
            $lux.log.error('Cannot handle form ready');
        };
        //
        // API base url
        api.baseUrl = function () {
            return url;
        };
        //
        api.get = function (opts, data) {
            return api.request('get', opts, data);
        };
        //
        api.post = function (opts, data) {
            return api.request('post', opts, data);
        };
        //
        api.put = function (opts, data) {
            return api.request('put', opts, data);
        };
        //
        api.head = function (opts, data) {
            return api.request('head', opts, data);
        };
        //
        api.delete = function (opts, data) {
            return api.request('delete', opts, data);
        };
        //
        //  Add additional Http options to the request
        api.httpOptions = function () {
        };
        //
        //  This function can be used to add authentication
        api.authentication = function () {
        };
        //
        //  Return the current user
        //  ---------------------------
        //
        //  Only implemented by apis managing authentication
        api.user = function () {
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
            if (ENCODE_URL_METHODS.indexOf(o.method) === -1) {
                o.data = data;
            } else {
                if (!angular.isObject(o.params)) {
                    o.params = {};
                }
                extend(o.params, data || {});
            }

            opts = extend(o, opts);

            var d = $lux.q.defer(),
            //
                request = {
                    name: opts.name,
                    //
                    deferred: d,
                    //
                    on: $lux.promise(d.promise, opts),
                    //
                    options: opts,
                    //
                    error: function (response) {
                        if (angular.isString(response.data))
                            response.data = {error: true, message: data};
                        d.reject(response);
                    },
                    //
                    success: function (response) {
                        if (angular.isString(response.data))
                            response.data = {message: data};

                        if (!response.data || response.data.error)
                            d.reject(response);
                        else
                            d.resolve(response);
                    }
                };
            //
            delete opts.name;
            if (opts.url === api.baseUrl())
                delete opts.url;
            //
            sendRequest(request);
            //
            return request.on;
        };

        /**
         * Populates $lux.apiUrls for an API URL.
         *
         * @returns      promise
         */
        api.populateApiUrls = function () {
            $lux.log.info('Fetching api info');
            return $lux.http.get(url).then(function (resp) {
                $lux.apiUrls[url] = resp.data;
                return resp.data;
            });
        };

        /**
         * Gets API endpoint URLs from root URL
         *
         * @returns     promise, resolved when API URLs available
         */
        api.getApiNames = function () {
            var promise, deferred;
            if (!angular.isObject($lux.apiUrls[url])) {
                promise = api.populateApiUrls();
            } else {
                deferred = $lux.q.defer();
                promise = deferred.promise;
                deferred.resolve($lux.apiUrls[url]);
            }
            return promise;
        };

        /**
         * Gets the URL for an API target
         *
         * @param target
         * @returns     promise, resolved when the URL is available
         */
        api.getUrlForTarget = function (target) {
            return api.getApiNames().then(function (apiUrls) {
                var url = apiUrls[target.name];
                if (target.path) {
                    url = lux.joinUrl(url, target.path);
                }
                return url;
            });
        };

        return api;
        //
        //  Execute an API call for a given request
        //  This method is hardly used directly,
        //	the ``request`` method is normally used.
        //
        //      request: a request object obtained from the ``request`` method
        function sendRequest (request) {
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
                    return api.populateApiUrls(url).then(function () {
                        sendRequest(request);
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
                    href = lux.joinUrl(request.baseUrl, opts.path);
                opts.url = href;
            }

            api.httpOptions(request);
            api.authentication(request);
            //
            var options = request.options;

            if (options.url) {
                $lux.log.info('Executing HTTP ' + options.method + ' request @ ' + options.url);
                $lux.http(options).then(request.success, request.error);
            }
            else
                request.error('Api url not available');
        }
    };

    return lux.apiFactory;

    //
    function _luxHttpPromise () {

        function luxHttpPromise (promise, options) {

            promise.options = function () {
                return options;
            };

            angular.forEach(luxHttpPromise, function (value, key) {
                promise[key] = value;
            });

            return promise;
        }

        luxHttpPromise.success = function (fn) {

            return luxHttpPromise(this.then(function (response) {
                var r = fn(response.data, response.status, response.headers);
                return angular.isUndefined(r) ? response : r;
            }), this.options());
        };

        luxHttpPromise.error = function (fn) {

            return luxHttpPromise(this.then(null, function (response) {
                var r = fn(response.data, response.status, response.headers);
                return angular.isUndefined(r) ? response : r;
            }), this.options());
        };

        return luxHttpPromise;
    }
});
