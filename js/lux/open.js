define(['jquery', 'angular'], function ($) {
    "use strict";

    var root = window,
        lux = {version: '0.1.0'},
        routes = [],
        ready_callbacks = [],
        require_callbacks = [],
        forEach = angular.forEach,
        angular_bootstrapped = false,
        context = root.luxContext || {},
        requires = [];

    root.lux = lux;
    angular.element = $;
    lux.$ = $;
    lux.forEach = angular.forEach;
    lux.context = context;
    lux.directiveOptions = root.luxDirectiveOptions || {};

    // Get directive options from the ``directiveOptions`` object
    lux.getDirectiveOptions = function (attrs) {
        if (typeof attrs.options === 'string') {
            attrs = $.extend(attrs, lux.directiveOptions[attrs.options]);
        }
        return attrs;
    };

    // Callbacks run after angular has finished bootstrapping
    lux.add_ready_callback = function (callback) {
        if (ready_callbacks === true) callback();
        else ready_callbacks.push(callback);
    };

    // Add a callback executed once all modules in the main page have been loaded
    lux.add_require_callback = function (callback) {
        require_callbacks.push(callback);
    };

    // Callback invoked by requirejs when all modules required in the main page have been loaded
    lux.lux_require_callback = function () {
        lux.add_ready_callback(function () {
            forEach(require_callbacks, function (callback) {
                callback();
            });
        });
    };
