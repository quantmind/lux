define(['jquery', 'angular', 'angular-route'], function ($) {
    "use strict";

    var lux = {},
        defaults = {},
        root = window,
        routes = [];
        context = angular.extend(defaults, root.context);

    lux.$ = $;
    lux.context = context;
    lux.services = angular.module('lux.services', []),
    lux.controllers = angular.module('lux.controllers', ['lux.services']);
    lux.app = angular.module('lux', ['ngRoute', 'lux.controllers', 'lux.services']);
    //
    // Callbacks run after angular has finished bootstrapping
    lux.ready_callbacks = [];

    // Add a new HTML5 route to the page router
    lux.addRoute = function (url, data) {
        routes.push([url, data]);
    };

    // Load angular
    angular.element(document).ready(function() {
        //
        if (routes.length && context.html5) {
            var rs = routes;
            routes = [];
            lux.setupRouter(rs);
        }
        angular.bootstrap(document, ['lux']);
        //
        var callbacks = lux.ready_callbacks;
        lux.ready_callbacks = [];
        angular.forEach(callbacks, function (callback) {
            callback();
        });
    });

    lux.setupRouter = function (routes) {
        //
        lux.app.config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider) {

            angular.forEach(routes, function (route) {
                var url = route[0];
                var data = route[1];
                if ($.isFunction(data)) data = data();
                $routeProvider.when('/', data);
            });
            // use the HTML5 History API
            $locationProvider.html5Mode(true);
        }]);
    };



    lux.controllers.controller('page', ['$scope', '$http', '$location', function ($scope, $http, $location) {
        angular.extend($scope, context);
        $scope.search_text = '';

        // logout via post method
        $scope.logout = function(e, url) {
            e.preventDefault();
            e.stopPropagation();
            $.post(url).success(function (data) {
                if (data.redirect)
                    window.location.replace(data.redirect);
            });
        };

        // Search
        $scope.search = function () {
            if ($scope.search_text) {
                window.location.href = '/search?' + $.param({q: $scope.search_text});
            }
        };

    }]);
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

    function formController ($scope, $element, $location, $http, model) {
        model || (model = {});

        $scope.formModel = model;
        $scope.formClasses = {};
        $scope.formErrors = {};

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
        };

        // process form
        $scope.processForm = function() {
            if ($scope.form.$invalid) {
                return $scope.showErrors();
            }

            var options = {
                url: $element.attr('action'),
                method: $element.attr('method') || 'POST',
                data: $scope.formModel
            };
            var enctype = $element.attr('enctype');
            if (enctype)
                options.headers = {
                    "Content-Type": enctype
                };
            // submit
            $http(options).success(function(data) {
                console.log(data);

                if (!data.success) {
                    // if not successful, bind errors to error variables
                    $scope.message = data.message;
                    if (data.errors) {
                        _(data.errors).forEach(function (obj) {
                            //$scope.errorName = data.errors.name;
                            //$scope.errorSuperhero = data.errors.superheroAlias;
                        });
                    } else if (data.html_url) {
                        window.location.href = data.html_url;
                    }
                } else {
                    // if successful, bind success message to message
                    $scope.message = data.message;
                }
            });
        };
    }

    // Controller for User
    lux.controllers.controller('userController', ['$scope', '$element', '$location', '$http',
            function ($scope, $element, $location, $http) {
        // Model for a user when updating
        formController($scope, $element, $location, $http);

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

	return lux;
});