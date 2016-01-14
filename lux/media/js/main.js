define(['angular',
        'lux/core'], function(angular, lux) {
    "use strict";

    var forEach = angular.forEach,
        extend = angular.extend,
        angular_bootstrapped = false,
        $ = angular.element,
        defaults = {
            url: '',    // base url for the web site
            MEDIA_URL: '',  // default url for media content
            hashPrefix: '',
            ngModules: []
        };

    //
    lux.version = '0.1.0';
    lux.forEach = angular.forEach;
    lux.context = extend({}, defaults, lux.context);

    lux.media = function (url, ctx) {
        if (!ctx)
            ctx = lux.context;
        return lux.joinUrl(ctx.url, ctx.MEDIA_URL, url);
    };

    lux.loader = angular.module('lux.loader', [])
    	//
        .value('context', lux.context)
        //
        .config(['$controllerProvider', function ($controllerProvider) {
            lux.loader.cp = $controllerProvider;
            lux.loader.controller = $controllerProvider;
        }])
        //
        .run(['$rootScope', '$log', '$timeout', 'context',
              	function (scope, $log, $timeout, context) {
            $log.info('Extend root scope with context');
            extend(scope, context);
            scope.$timeout = $timeout;
            scope.$log = $log;
        }]);
    //
    //  Bootstrap the document
    //  ============================
    //
    //  * ``name``  name of the module
    //  * ``modules`` modules to include
    //
    //  These modules are appended to the modules available in the
    //  lux context object and therefore they will be processed afterwards.
    //
    lux.bootstrap = function (name, modules) {
        //
        // actual bootstrapping function
        function _bootstrap() {
            //
            // Resolve modules to load
            var mods = lux.context.ngModules;
            if(!mods) mods = [];

            // Add all modules from input
            forEach(modules, function (mod) {
                mods.push(mod);
            });
            // Insert the lux loader as first module
            mods.splice(0, 0, 'lux.loader');
            angular.module(name, mods);
            angular.bootstrap(document, [name]);
        }

        if (!angular_bootstrapped) {
            angular_bootstrapped = true;
            //
            $(document).ready(function() {
                _bootstrap();
            });
        }
    };

    return lux;
});
