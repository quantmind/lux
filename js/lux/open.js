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

    lux._setupRouter = function (routes) {
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
