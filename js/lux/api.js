    var ApiTypes = lux.ApiTypes = {};
    //
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
    lux.services.service('$lux', function ($location, $q, $http, $log, $anchorScroll) {
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
        //  context: an api name or an object containing, name, url and type.
        //
        //  name: the api name
        //  url: the api base url
        //  type: optional api type (default is ``lux``)
        this.api = function (context) {
            if (Object(context) !== context) {
                context = {name: context};
            }
            var provider = ApiTypes[context.type || 'lux'];
            if (!provider) {
                $lux.log.error('Api provider "' + context.type + '" is not available');
            }
            return provider.api(context.name, context.url, $lux);
        };

    });
    //  The provider actually implements the comunication layer
    //
    //  Lux Provider is for an API built using Lux
    //
    var BaseApi = {
        //
        //  Object containing the urls for the api.
        //  If not given, the object will be loaded via the ``context.apiUrl``
        //  variable.
        apiUrls: context.apiUrls,
        //
        api: function (name, url, $lux) {
            return new LuxApi(name, url, this, $lux);
        },
        //
        //  Handle authentication
        //
        //  By default does nothing
        authentication: function (request) {
            this.auth = {};
            this.call(request);
        },
        //
        // Add Authentication to call options
        addAuth: function (request) {

        },
        //
        httpOptions: function (request) {
            var options = request.options,
                url = options.url;
            if ($.isFunction(url)) url = url();
            if (!url) url = request.api.url;
            options.url = url;
            return options;
        },
        //
        // Internal method for executing an API call
        call: function (request) {
            var self = this,
                api = request.api,
                $lux = api.lux;
            //
            if (!api.url && ! api.name) {
                return request.error('api should have url or name');
            }

            if (!api.url) {
                if (this.apiUrls) {
                    api.url = this.apiUrls[api.name] || this.apiUrls[api.name + '_url'];
                    //
                    // No api url!
                    if (!api.url)
                        return request.error('Could not find a valid url for ' + api.name);
                    //
                } else if (context.apiUrl) {
                    // Fetch the api urls
                    $lux.log.info('Fetching api info');
                    return $lux.http.get(context.apiUrl).success(function (resp) {
                        self.apiUrls = resp;
                        self.call(request);
                    }).error(request.error);
                    //
                } else
                    return request.error('Api url not available');
            }
            //
            // Fetch authentication token?
            if (!self.auth)
                return self.authentication(request);
            //
            // Add authentication
            self.addAuth(request);
            //
            var options = self.httpOptions(request);
            //
            $lux.http(options).success(request.success).error(request.error);
        }
    };
    //
    //
    lux.createApi = function (name, object) {
        //
        ApiTypes[name] = angular.extend({}, BaseApi, object);
        //
        return ApiTypes[name];
    };
    //
    //  Lux Default API
    //  ----------------------
    //
    lux.createApi('lux', {
        //
        authentication: function (request) {
            var self = this;
            //
            if (context.user) {
                $lux.log.info('Fetching authentication token');
                //
                $lux.post('/_token').success(function (data) {
                    self.auth = {user_token: data.token};
                    self.call(request);
                }).error(request.error);
                //
                return request.deferred.promise;
            } else {
                self.auth = {};
                self.call(request);
            }
        },
        //
        addAuth: function (api, options) {
            //
                    // Add authentication token
            if (this.user_token) {
                var headers = options.headers;
                if (!headers)
                    options.headers = headers = {};

                headers.Authorization = 'Bearer ' + this.user_token;
            }
        }
    });
    //
    //  Lux Static JSON API
    //  ----------------------
    lux.createApi('static', {
        //
        httpOptions: function (request) {
            var options = request.options,
                url = request.api.url,
                path = request.urlparams.path;
            if (path)
                url += '/' + path;
            if (url.substring(url.length-5) !== '.json')
                url += '.json';
            options.url = url;
            return options;
        }
    });
    //
    //  LuxApi
    //  --------------
    //
    //  Interface for accessing apis
    function LuxApi(name, url, provider, $lux) {
        var self = this;

        this.lux = $lux;
        this.name = name;
        this.url = url;
        this.auth = null;
        //
        // Perform the actual request
        this.request = function (method, urlparams, opts) {
            var d = $lux.q.defer(),
                //
                promise = d.promise,
                //
                request = {
                    deferred: d,
                    //
                    options: angular.extend({'method': method}, opts),
                    //
                    'urlparams': urlparams,
                    //
                    api: self,
                    //
                    error: function (data, status, headers) {
                        if (angular.isString(data)) {
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
                        d.resolve({
                            'data': data,
                            'status': status,
                            'headers': headers
                        });
                    }
                };
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

            provider.call(request);
            //
            return promise;
        };
        //
        //  Get a single element
        //  ---------------------------
        this.get = function (urlparams, options) {
            return self.request('GET', urlparams, options);
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
            return self.request(options);
        };

        //  Get a list of models
        //  -------------------------
        this.getMany = function (options) {
            return self.request(angular.extend({
                method: 'GET'
            }, options));
        };
    }