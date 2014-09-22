define(['jquery', 'angular', 'angular-sanitize'], function ($) {
    "use strict";

    var lux = {},
        defaults = {
            ngModules: [],
            ngDirectives: [],
            ngControllers: []
        },
        root = window,
        routes = [],
        ready_callbacks = [],
        angular_bootstrapped = false,
        // extend the context from the global variable context
        context = $.extend(defaults, root.context);

    // when in html5 mode add ngRoute to the list of required modules
    if (context.html5mode)
        context.ngModules.push('ngRoute');

    angular.element = $;
    lux.$ = $;
    lux.forEach = angular.forEach;
    lux.context = context;
    lux.services = angular.module('lux.services', []);
    lux.controllers = angular.module('lux.controllers', ['lux.services']);
    lux.app = angular.module('lux', []);
    lux.directiveOptions = root.luxDirectiveOptions || {};

    // Get directive options from the ``directiveOptions`` object
    lux.getDirectiveOptions = function (attrs) {
        if (typeof attrs.options === 'string') {
            attrs = $.extend(attrs, lux.directiveOptions[attrs.options]);
        }
        return attrs;
    };

    // Add a new HTML5 route to the page router
    lux.addRoute = function (url, data) {
        routes.push([url, data]);
    };

    // Callbacks run after angular has finished bootstrapping
    lux.add_ready_callback = function (callback) {
        if (ready_callbacks === true) callback();
        else ready_callbacks.push(callback);
    };

    $.each(['ngSanitize', 'lux.controllers', 'lux.services'], function (i, name) {
        context.ngModules.push(name);
    });
