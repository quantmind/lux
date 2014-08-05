define(['jquery', 'angular', 'angular-sanitize'], function ($) {
    "use strict";

    var lux = {},
        defaults = {},
        root = window,
        routes = [],
        ready_callbacks = [],
        context = $.extend(defaults, root.context),
        ngModules = ['ngSanitize', 'lux.controllers', 'lux.services'];

    // when in html5 mode add ngRoute to the list of required modules
    if (context.html5mode)
        ngModules.push('ngRoute');

    angular.element = $;
    lux.$ = $;
    lux.context = context;
    lux.services = angular.module('lux.services', []);
    lux.controllers = angular.module('lux.controllers', ['lux.services']);
    lux.app = angular.module('lux', ngModules);

    // Add a new HTML5 route to the page router
    lux.addRoute = function (url, data) {
        routes.push([url, data]);
    };

    // Callbacks run after angular has finished bootstrapping
    lux.add_ready_callback = function (callback) {
        if (ready_callbacks === true) callback();
        else ready_callbacks.push(callback);
    };

    lux.requiresAngular = function () {
        lux.$.each(arguments, function (i, module) {
            if (lux.app.requires.indexOf(module) === -1)
                lux.app.requires.push(module);
        });
    };
