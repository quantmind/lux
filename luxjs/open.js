(function (factory) {
    var root = this;
    if (typeof module === "object" && module.exports)
        root = module.exports;
    //
    if (typeof define === 'function' && define.amd) {
        // Support AMD. Register as an anonymous module.
        // NOTE: List all dependencies in AMD style
        define(['angular'], function (angular) {
            root.lux = factory(angular, root);
            return root.lux;
        });
    } else {
        // No AMD. Set module as a global variable
        // NOTE: Pass dependencies to factory function
        // (assume that angular is also global.)
        root.lux = factory(angular, root);
    }
}(
function(angular, root) {
    "use strict";

    var lux = root.lux || {};
    lux.version = '0.1.0';

    var forEach = angular.forEach,
        extend = angular.extend,
        angular_bootstrapped = false,
        isArray = angular.isArray,
        isString = angular.isString,
        $ = angular.element,
        slice = Array.prototype.slice,
        lazyApplications = {},
        defaults = {
            url: '',    // base url for the web site
            MEDIA_URL: '',  // default url for media content
            hashPrefix: '!',
            ngModules: []
        };
    //
    lux.$ = $;
    lux.angular = angular;
    lux.forEach = angular.forEach;
    lux.context = extend({}, defaults, lux.context);

    // Extend lux context with additional data
    lux.extend = function (context) {
        lux.context = extend(lux.context, context);
        return lux;
    };

    lux.media = function (url, ctx) {
        if (!ctx)
            ctx = lux.context;
        return joinUrl(ctx.url, ctx.MEDIA_URL, url);
    };

    lux.luxApp = function (name, App) {
        lazyApplications[name] = App;
    };

    angular.module('lux.applications', ['lux.services'])

        .directive('luxApp', ['$lux', function ($lux) {
            return {
                restrict: 'AE',
                //
                link: function (scope, element, attrs) {
                    var options = getOptions(attrs),
                        appName = options.luxApp;
                    if (appName) {
                        var App = lazyApplications[appName];
                        if (App) {
                            options.scope = scope;
                            var app = new App(element[0], options);
                            scope.$emit('lux-app', app);
                        } else {
                            $lux.log.error('Application ' + appName + ' not registered');
                        }
                    } else {
                        $lux.log.error('Application name not available');
                    }
                }
            };
        }]);

    lux.context.ngModules.push('lux.applications');