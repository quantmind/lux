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

    lux.bootstrap = function () {
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
