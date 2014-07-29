    // If CSRF token is not available
    // try to obtain it from the meta tags
    if (!context.csrf) {
        var name = $("meta[name=csrf-param]").attr('content'),
            token = $("meta[name=csrf-token]").attr('content');
        if (name && token) {
            context.csrf = {};
            context.csrf[name] = token;
        }
    }
    //  Lux Api service factory for angular
    //  ---------------------------------------
    //
    lux.services.service('$lux', function ($location, $q, $http, $log) {
        var $lux = this;

        this.location = $location;
        this.log = $log;
        this.http = $http;
        this.q = $q;

        // A post method with CSRF parameter
        this.post = function (url, data, cfg) {
            if (context.csrf) {
                data || (data = {});
                angular.extend(data, context.csrf);
            }
            return $http.post(url, data, cfg);
        };

        //  Create an api client
        //  -------------------------
        //
        //  name: the api name
        //  provider: optional provider
        this.api = function (name, provider) {
            if (!provider) provider = LuxApiProvider;
            return provider.api(name, $lux);
        };

    });

    //  The provider actually implements the comunication layer
    //
    //  Lux Provider is for an API built using Lux
    //
    var LuxApiProvider = {
        //
        //  Object containing the urls for the api.
        //  If not given, the object will be loaded via the ``context.apiUrl``
        //  variable.
        apiUrls: context.apiUrls,
        //
        api: function (name, $lux) {
            return new LuxApi(name, this, $lux);
        },
        //
        // Internal method for executing an API call
        call: function (api, options, callback, deferred) {
            var self = this,
                $lux = api.lux;
            //
            // First time here, build the deferred
            if (!deferred)
                deferred = $lux.q.defer();

            function _error (data, status, headers) {
                deferred.reject({
                    'data': data,
                    'status': status,
                    'headers': headers
                });
            }

            if (this.apiUrls) {
                var api_url = this.apiUrls[api.name] || this.apiUrls[api.name + '_url'];
                //
                // No api url!
                if (!api_url) {
                    deferred.reject({
                        error: true,
                        message: 'Could not find a valid url for ' + api.name
                    });
                //
                // Fetch authentication token
                } else if (this.user_token === undefined && context.user) {
                    $lux.log.info('Fetching authentication token');
                    $lux.post('/_token').success(function (data) {
                        self.user_token = data.token || null;
                        self.call(api, options, callback, deferred);
                    }).error(_error);
                //
                // Make the api call
                } else {
                    //
                    // Add authentication token
                    if (this.user_token) {
                        var headers = options.headers;
                        if (!headers)
                            options.headers = headers = {};

                        headers.Authorization = 'Bearer ' + this.user_token;
                    }
                    //
                    // Build url from ``options.url`` which can be a function
                    var url = options.url;
                    if ($.isFunction(url)) url = url(api_url);
                    if (!url) url = api_url;
                    options.url = url;
                    //
                    $lux.http(options).success(function (data, status, headers) {
                        data = callback ? callback(data) : data;
                        deferred.resolve({
                            'data': data,
                            'status': status,
                            'headers': headers
                        });
                    }).error(_error);
                }
            } else if (context.apiUrl) {
                // Fetch the api urls
                $lux.log.info('Fetching api info');
                $lux.http.get(context.apiUrl).success(function (resp) {
                    self.apiUrls = resp;
                    self.call(api, options, callback, deferred);
                }).error(_error);
            } else {
                deferred.resolve({
                    data: {
                        'message': 'Api url not available',
                        'error': true
                    }
                });
            }
            //
            var promise = deferred.promise;
            //
            promise.success = function(fn) {
                promise.then(function(response) {
                    fn(response.data, response.status, response.headers);
                });
                return promise;
            };

            promise.error = function(fn) {
                promise.then(null, function(response) {
                    fn(response.data, response.status, response.headers);
                });
                return promise;
            };
            //
            return promise;
        }
    };

    //
    //  LuxApi
    //  --------------
    function LuxApi(name, provider, $lux) {
        var self = this;

        this.lux = $lux;
        this.name = name;

        //  Get a single element
        //  ---------------------------
        this.get = function (params, options) {
            options = angular.extend({
                url: function (url) {
                    var path = '';
                    if (Object(params) === params) {
                        angular.forEach(params, function (name, value) {
                            path = '/' + value;
                        });
                    } else if (params) {
                        path = '/' + params;
                    }
                    if (path) {
                        if (url.substring(url.length-1) === '/')
                            url = url.substring(0, url.length-1);
                        return url + path;
                    } else {
                        return url;
                    }
                },
                method: 'GET'
            }, options);
            return provider.call(self, options);
        };

        //  Create or update a model
        //  ---------------------------
        this.put = function (model, options) {
            if (model.id) {
                options = angular.extend({
                    url: function (url) {
                        return url + '/' + model.id;
                    },
                    data: model,
                    method: 'POST'}, options);
            } else {
                options = angular.extend({
                    data: model,
                    method: 'POST'}, options);
            }
            return provider.call(self, options);
        };

        //  Get a list of models
        //  -------------------------
        this.getMany = function (options) {
            options = angular.extend({method: 'GET'}, options);
            return provider.call(self, options);
        };

    }