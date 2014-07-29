define(['jquery', 'angular', 'angular-route', 'angular-sanitize'], function ($) {
    "use strict";

    var lux = {},
        defaults = {},
        root = window,
        routes = [],
        ready_callbacks = [],
        context = $.extend(defaults, root.context);

    angular.element = $;
    lux.$ = $;
    lux.context = context;
    lux.services = angular.module('lux.services', []);
    lux.controllers = angular.module('lux.controllers', ['lux.services']);
    lux.app = angular.module('lux', ['ngRoute', 'ngSanitize', 'lux.controllers', 'lux.services']);

    // Add a new HTML5 route to the page router
    lux.addRoute = function (url, data) {
        routes.push([url, data]);
    };

    // Callbacks run after angular has finished bootstrapping
    lux.add_ready_callback = function (callback) {
        if (ready_callbacks === true) callback();
        else ready_callbacks.push(callback);
    };

    lux._setupRouter = function (all) {
        //
        lux.app.config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider) {

            angular.forEach(all, function (route) {
                var url = route[0];
                var data = route[1];
                if ($.isFunction(data)) data = data();
                $routeProvider.when(url, data);
            });
            // use the HTML5 History API
            $locationProvider.html5Mode(true);
        }]);
    };

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

    // Page Controller
    //
    // Handle html5 sitemap
    lux.controllers.controller('page', ['$scope', '$lux', function ($scope, $lux) {
        //
        $lux.log.info('Setting up angular page');
        //
        angular.extend($scope, context);
        var page = $scope.page;
        if (page && $scope.pages) {
            $scope.page = page = $scope.pages[page];
        } else {
            $scope.page = page = {};
        }
        //
        $scope.search_text = '';
        $scope.sidebar_collapse = '';
        //
        // logout via post method
        $scope.logout = function(e, url) {
            e.preventDefault();
            e.stopPropagation();
            $lux.post(url).success(function (data) {
                if (data.redirect)
                    window.location.replace(data.redirect);
            });
        };
        //
        // Search
        $scope.search = function () {
            if ($scope.search_text) {
                window.location.href = '/search?' + $.param({q: $scope.search_text});
            }
        };

        // Dismiss a message
        $scope.dismiss = function (m) {
            $lux.post('/_dismiss_message', {message: m});
        };

        $scope.togglePage = function ($event) {
            $event.preventDefault();
            $event.stopPropagation();
            this.link.active = !this.link.active;
        };

        $scope.loadPage = function ($event) {
            $scope.page = this.link;
        };

        $scope.collapse = function () {
            var width = root.window.innerWidth > 0 ? root.window.innerWidth : root.screen.width;
            if (width < context.collapse_width)
                $scope.sidebar_collapse = 'collapse';
            else
                $scope.sidebar_collapse = '';
        };

        $scope.collapse();
        $(root).bind("resize", function () {
            $scope.collapse();
            $scope.$apply();
        });

    }]);

    lux.controllers.controller('html5Page', ['$scope', '$lux', 'data',
        function ($scope, $lux, data) {
            if (content.title) {
                document.title = data.title;
            }
            $scope.content = data.content;
    }]);
    //  SITEMAP
    //  -----------------
    //
    //  Build an HTML5 sitemap when the ``context.sitemap`` variable is set.
    function _load_sitemap (hrefs, pages) {
        //
        angular.forEach(hrefs, function (href) {
            var page = pages[href];
            if (page && page.href && page.target !== '_self') {
                lux.addRoute(page.href, route_config(page));
            }
        });
    }

    function route_config (page) {

        return {
            templateUrl: function (obj) {
                var url = page.template_url;
                angular.forEach(page.template_url_vars, function (name) {
                    var r = obj[name] || '';
                    url = url.replace(':' + name, r);
                });

                return url;
            },
            controller: page.controller || 'page',
            resolve: {
                data: function ($lux, $route) {
                    if (page.api) {
                        var api = $lux.api(page.api, page.api_provider);
                        return api.get($route.current.params);
                    }
                }
            }
        };
    }
    //
    // Load sitemap if available
    _load_sitemap(context.hrefs, context.pages);

    var FORMKEY = 'm__form';
    //
    // add the watch change directive
    lux.app.directive('watchChange', function() {
        return {
            scope: {
                onchange: '&watchChange'
            },
            //
            link: function(scope, element, attrs) {
                element.on('keyup', function() {
                    scope.$apply(function () {
                        scope.onchange();
                    });
                }).on('change', function() {
                    scope.$apply(function () {
                        scope.onchange();
                    });
                });
            }
        };
    });

    // Change the form data depending on content type
    function formData(ct) {

        return function (data, getHeaders ) {
            angular.extend(data, context.csrf);
            if (ct === 'application/x-www-form-urlencoded')
                return $.param(data);
            else if (ct === 'multipart/form-data') {
                var fd = new FormData();
                angular.forEach(data, function (value, key) {
                    fd.append(key, value);
                });
                return fd;
            } else {
                return data;
            }
        };
    }

    // A general from controller factory
    function formController ($scope, $lux, model) {
        model || (model = {});

        var page = $scope.$parent ? $scope.$parent.page : {};

        $scope.formModel = model.data || model;
        $scope.formClasses = {};
        $scope.formErrors = {};
        $scope.formMessages = {};

        if ($scope.formModel.name) {
            page.title = 'Update ' + $scope.formModel.name;
        }

        function formMessages (messages) {
            angular.forEach(messages, function (messages, field) {
                $scope.formMessages[field] = messages;
            });
        }

        $scope.checkField = function (name) {
            var checker = $scope['check_' + name];
            // There may be a custom field checker
            if (checker)
                checker.call($scope);
            else {
                var field = $scope.form[name];
                if (field.$valid)
                    $scope.formClasses[name] = 'has-success';
                else if (field.$dirty) {
                    $scope.formErrors[name] = name + ' is not valid';
                    $scope.formClasses[name] = 'has-error';
                }
            }
        };

        // display field errors
        $scope.showErrors = function () {
            var error = $scope.form.$error;
            angular.forEach(error.required, function (e) {
                $scope.formClasses[e.$name] = 'has-error';
            });
        };

        // process form
        $scope.processForm = function($event) {
            $event.preventDefault();
            $event.stopPropagation();
            var $element = angular.element($event.target),
                apiname = $element.attr('data-api'),
                target = $element.attr('action'),
                promise,
                api;
            //
            if ($scope.form.$invalid) {
                return $scope.showErrors();
            }

            // Get the api information
            if (!target && apiname) {
                api = $lux.api(apiname);
                if (!api)
                    $lux.log.error('Could not find api url for ' + apiname);
            }

            $scope.formMessages = {};
            //
            if (target) {
                var enctype = $element.attr('enctype') || '',
                    ct = enctype.split(';')[0],
                    options = {
                        url: target,
                        method: $element.attr('method') || 'POST',
                        data: $scope.formModel,
                        transformRequest: formData(ct),
                    };
                // Let the browser choose the content type
                if (ct === 'application/x-www-form-urlencoded' || ct === 'multipart/form-data') {
                    options.headers = {
                        'content-type': undefined
                    };
                }
                promise = $lux.http(options);
            } else if (api) {
                promise = api.put($scope.formModel);
            } else {
                $lux.log.error('Could not process form. No target or api');
                return;
            }

            //
            promise.success(function(data, status) {
                if (data.messages) {
                    angular.forEach(data.messages, function (messages, field) {
                        $scope.formMessages[field] = messages;
                    });
                } else if (api) {
                    // Created
                    if (status === 201) {
                        $scope.formMessages[FORMKEY] = [{message: 'Succesfully created'}];
                    } else {
                        $scope.formMessages[FORMKEY] = [{message: 'Succesfully updated'}];
                    }
                } else {
                    window.location.href = data.redirect || '/';
                }
            }).error(function(data, status, headers) {
                var messages, msg;
                if (data) {
                    messages = data.messages;
                    if (!messages) {
                        msg = data.message;
                        if (!msg) {
                            status = status || data.status || 501;
                            msg = 'Server error (' + data.status + ')';
                        }
                        messages = {};
                        messages[FORMKEY] = [{message: msg, error: true}];
                    }
                } else {
                    status = status || 501;
                    msg = 'Server error (' + data.status + ')';
                    messages = {};
                    messages[FORMKEY] = [{message: msg, error: true}];
                }
                formMessages(messages);
            });
        };
    }

    lux.controllers.controller('formController', ['$scope', '$lux', 'data',
            function ($scope, $lux, data) {
        // Model for a user when updating
        formController($scope, $lux, data);
    }]);


    lux.controllers.controller('listgroup', ['$scope', '$lux', 'data', function ($scope, $lux, data) {
        $scope.data = data.data;
    }]);


    // Controller for User
    lux.controllers.controller('userController', ['$scope', '$lux', function ($scope, $lux) {
        // Model for a user when updating
        formController($scope, $lux, context.user);

        // Unlink account for a OAuth provider
        $scope.unlink = function(e, name) {
            e.preventDefault();
            e.stopPropagation();
            var url = '/oauth/' + name + '/remove';
            $.post(url).success(function (data) {
                if (data.success)
                    $route.reload();
            });
        };

        // Check if password is correct
        $scope.check_password_repeat = function () {
            var u = this.formModel,
                field = this.form.password_repeat,
                psw1 = u.password,
                psw2 = u.password_repeat;
            if (psw1 !== psw2 && field.$dirty) {
                this.formErrors.password_repeat = "passwords don't match";
                field.$error.password_repeat = true;
                this.formClasses.password_repeat = 'has-error';
            } else if (field.$dirty) {
                this.formClasses.password_repeat = 'has-success';
                delete this.form.$error.password_repeat;
            }
        };

    }]);
    //
    lux.bootstrap = function () {
        //
        $(document).ready(function() {
            //
            if (routes.length && context.html5mode) {
                var rs = routes;
                routes = [];
                lux._setupRouter(rs);
            }
            //
            angular.bootstrap(document, ['lux']);
            //
            angular.forEach(ready_callbacks, function (callback) {
                callback();
            });
            ready_callbacks = true;
        });
    };

	return lux;
});