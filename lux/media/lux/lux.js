define(['jquery', 'angular', 'angular-route', 'angular-sanitize'], function ($) {
    "use strict";

    var lux = {},
        defaults = {},
        root = window,
        routes = [],
        ready_callbacks = [],
        context = angular.extend(defaults, root.context);

    lux.$ = $;
    lux.context = context;
    lux.services = angular.module('lux.services', []),
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

    lux.bootstrap = function () {
        angular.element(document).ready(function() {
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


    var LuxApis = {};

    //  Lux Api service factory for angular
    //  ---------------------------------------
    //
    lux.services.service('$lux', function ($location, $q, $http, $log) {
        var $lux = this;

        this.location = $location;
        this.log = $log;
        this.http = $http;
        this.q = $q;

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
        api: function (name, $lux) {
            return new LuxApi(name, this, $lux);
        },
        //
        call: function (api, options, callback, deferred) {
            var self = this,
                $lux = api.lux;
            //
            if (!deferred)
                deferred = $lux.q.defer();

            function _error (data, status, headers) {
                deferred.reject(data, status, headers);
            }

            if (this._api) {
                var api_url = this._api[api.name + '_url'];
                if (!api_url)
                    deferred.reject('Could not find a valid url for ' + api.name);
                else if (this.user_token === undefined && context.user) {
                    $lux.log.info('Fetching authentication token');
                    $lux.http.post('/_token').success(function (resp) {
                        self.user_token = resp.token || null;
                        self.call(api, options, callback, deferred);
                    }).error(_error);
                } else {
                    //
                    // Make the call
                    if (this.user_token) {
                        var headers = options.headers;
                        if (!headers)
                            options.headers = headers = {};

                        headers.Authorization = 'Bearer ' + this.user_token;
                    }
                    var url = options.url;
                    if ($.isFunction(url)) url = url(api_url);
                    if (!url) url = api_url;
                    options.url = url;
                    //
                    $lux.http(options).success(function (resp) {
                        deferred.resolve(callback ? callback(resp) : resp);
                    }).error(_error);
                }
            } else if (context.apiUrl) {
                // Fetch the api urls
                $lux.log.info('Fetching api info');
                $lux.http.get(context.apiUrl).success(function (resp) {
                    self._api = resp;
                    self.call(api, options, callback, deferred);
                }).error(_error);
            } else {
                deferred.resolve({'message': 'Api url not available'});
            }
            //
            return deferred.promise;
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
        this.get = function (id, options) {

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
    lux.controllers.controller('page', ['$scope', '$http', '$location', function ($scope, $http, $location) {
        angular.extend($scope, context);
        $scope.search_text = '';
        $scope.page = context.page || {};
        $scope.sidebar_collapse = '';
        //
        // logout via post method
        $scope.logout = function(e, url) {
            e.preventDefault();
            e.stopPropagation();
            $.post(url).success(function (data) {
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
            $http.post('/_dismiss_message', m);
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

    //  SITEMAP
    //
    function _load_sitemap (sitemap) {
        angular.forEach(sitemap, function (page) {
            _load_sitemap(page.links);
            if (page.href && page.target !== '_self') {
                lux.addRoute(page.href, {
                    templateUrl: page.href + '/html'
                });
            }
        });
    }
    //
    // Load sitemap if available
    _load_sitemap(context.sitemap);


    var FORMKEY = 'm__form';
    //
    // add the watch change directive
    lux.app.directive('watchChange', function() {
        return {
            scope: {
                onchange: '&watchChange'
            },
            link: function(scope, element, attrs) {
                element.on('keyup', function() {
                    scope.$apply(function () {
                        scope.onchange();
                    });
                });
                element.on('change', function() {
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
            if (ct === 'application/x-www-form-urlencoded')
                return $.param(options.data);
            else if (ct === 'multipart/form-data') {
                var fd = new FormData();
                angular.forEach(data, function (value, key) {
                    fd.append(key, value);
                });
                return fd;
            } else return data;
        };
    }

    // A general from controller factory
    function formController ($scope, $lux, model) {
        model || (model = {});

        $scope.formModel = model;
        $scope.formClasses = {};
        $scope.formErrors = {};
        $scope.formMessages = {};

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
            promise.then(
                function(data) {
                    if (data.messages) {
                        angular.forEach(data.messages, function (messages, field) {
                            $scope.formMessages[field] = messages;
                        });
                    } else {
                        window.location.href = data.redirect || '/';
                    }
                },
                function(data, status, headers) {
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

    lux.controllers.controller('formController', ['$scope', '$lux',
            function ($scope, $lux) {
        // Model for a user when updating
        formController($scope, $lux);
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
	return lux;
});