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
    function formController ($scope, $location, $http, $sce, model) {
        model || (model = {});

        $scope.formModel = model;
        $scope.formClasses = {};
        $scope.formErrors = {};
        $scope.formMessages = {};

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
            var $element = angular.element($event.target);
            //
            if ($scope.form.$invalid) {
                return $scope.showErrors();
            }

            var enctype = $element.attr('enctype') || '',
                ct = enctype.split(';')[0],
                options = {
                    url: $element.attr('action'),
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
            //
            $scope.formMessages = {};
            //
            // submit
            $http(options).success(function(data) {
                if (data.messages) {
                    angular.forEach(data.messages, function (messages, field) {
                        $scope.formMessages[field] = messages;
                    });
                } else {
                    window.location.href = data.redirect || '/';
                }
            }).error(function(data, status, headers, config) {
            });
        };
    }

    lux.controllers.controller('formController', ['$scope', '$location', '$http', '$sce',
            function ($scope, $location, $http, $sce) {
        // Model for a user when updating
        formController($scope, $location, $http, $sce);
    }]);


    // Controller for User
    lux.controllers.controller('userController', ['$scope', '$location', '$http', '$sce',
            function ($scope, $location, $http, $sce) {
        // Model for a user when updating
        formController($scope, $location, $http, $sce, context.user);

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