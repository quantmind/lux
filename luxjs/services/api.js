    //  Lux Api service factory for angular
    //  ---------------------------------------
    angular.module('lux.api', [])
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
            this.api = function (context) {
                if (Object(context) !== context) {
                    context = {name: context};
                }
                var Api = ApiTypes[context.type || 'lux'];
                if (!Api)
                    $lux.log.error('Api provider "' + context.name + '" is not available');
                else
                    return new Api(context.name, context.url, context.options, $lux);
            };
            //
            this.registerApi = function (name, object, inheritFrom) {
                var Base = inheritFrom ? ApiTypes[inheritFrom] : ApiClient;
                ApiTypes[name] = Base.extend(object);
                return ApiTypes[name];
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
    var ApiClient = lux.ApiClient = Class.extend({
        //
        //  Object containing the urls for the api.
        //  If not given, the object will be loaded via the ``context.apiUrl``
        //  variable.
        apiUrls: lux.context.apiUrls,
        //
        init: function (name, url, options, $lux) {
            this.name = name;
            this.options = options || {};
            this.$lux = $lux;
            this.auth = null;
            this._url = url;
        },
        //
        // Can be used to manipulate the url
        url: function (urlparams) {
            if (urlparams && urlparams.id)
                return this._url + '/' + urlparams.id;
            else
                return this._url;
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
        // Build the object used by $http when executing the api call
        httpOptions: function (request) {
            var options = request.options;
            options.url = this.url(request.urlparams);
            return options;
        },
        //
        //
        // Perform the actual request and return a promise
        //  method: HTTP method
        //  urlparams:
        //  opts: object passed to
        request: function (method, urlparams, opts, data) {
            // handle urlparams when not an object
            if (urlparams && urlparams!==Object(urlparams))
                urlparams = {id: urlparams};

            var d = this.$lux.q.defer(),
                //
                promise = d.promise,
                //
                request = {
                    deferred: d,
                    //
                    options: extend({'method': method, 'data': data}, opts),
                    //
                    'urlparams': urlparams,
                    //
                    api: this,
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
                        d.resolve({
                            'data': data,
                            'status': status,
                            'headers': headers
                        });
                    }
                };
            //
            this.call(request);
            //
            return wrapPromise(promise);
        },
        //
        //  Get a single element
        //  ---------------------------
        get: function (urlparams, options) {
            return this.request('GET', urlparams, options);
        },
        //  Create or update a model
        //  ---------------------------
        put: function (model, options) {
            if (model.id) {
                return this.request('POST', {id: model.id}, options, model);
            } else {
                return this.request('POST', null, options, model);
            }
        },
        //  Get a list of models
        //  -------------------------
        getList: function (options) {
            return this.request('GET', null, options);
        },
        //
        getPage: function (page, state, stateParams) {
            return page;
        },
        //
        getItems: function (page, state, stateParams) {
            if (!lux.size(stateParams))
                return this.getList();
        },
        //
        //  Execute an API call for a given request
        //  This method is hardly used directly, the ``request`` method is normally used.
        //
        //      request: a request object obtained from the ``request`` method
        call: function (request) {
            var $lux = this.$lux;
            //
            if (!this._url && ! this.name) {
                return request.error('api should have url or name');
            }

            if (!this._url) {
                if (this.apiUrls) {
                    this._url = this.apiUrls[this.name] || this.apiUrls[this.name + '_url'];
                    //
                    // No api url!
                    if (!this.url)
                        return request.error('Could not find a valid url for ' + this.name);
                    //
                } else if (lux.context.apiUrl) {
                    // Fetch the api urls
                    var self = this;
                    $lux.log.info('Fetching api info');
                    return $lux.http.get(lux.context.apiUrl).success(function (resp) {
                        self.apiUrls = resp;
                        self.call(request);
                    }).error(request.error);
                    //
                } else
                    return request.error('Api url not available');
            }
            //
            // Fetch authentication token?
            if (!this.auth)
                return this.authentication(request);
            //
            // Add authentication
            this.addAuth(request);
            //
            var options = this.httpOptions(request);
            //
            if (options.url) {
                $lux.log.info('Executing HTTP ' + options.method + ' request @ ' + options.url);
                $lux.http(options).success(request.success).error(request.error);
            }
            else
                request.error('Api url not available');
        }
    });
