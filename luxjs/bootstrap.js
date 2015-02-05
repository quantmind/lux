    lux.loader = angular.module('lux.loader', []);

    lux.loader
        .value('context', lux.context)
        //
        .config(['$controllerProvider', function ($controllerProvider) {
            lux.loader.cp = $controllerProvider;
            lux.loader.controller = $controllerProvider;
        }])
        //
        .run(['$rootScope', '$log', '$timeout', 'context', function (scope, $log, $timeout, context) {
            $log.info('Extend root scope with context');
            extend(scope, context);
            scope.$timeout = $timeout;
            scope.$log = $log;
        }]);
    //
    // Bootstrap the document
    lux.bootstrap = function (name, modules) {
        //
        // actual bootstrapping function
        function _bootstrap() {
            //
            // Resolve modules to load
            if (!isArray(modules))
                modules = [];
            if (lux.context.uiRouter) {
                modules.push(lux.context.uiRouter);
                // Remove seo view, we don't want to bootstrap it
                $(document.querySelector('#seo-view')).remove();
            }
            else {
                modules.push('lux.router');
            }
            // Add all modules from context
            forEach(lux.context.ngModules, function (mod) {
                modules.push(mod);
            });
            modules.splice(0, 0, 'lux.loader');
            angular.module(name, modules);
            angular.bootstrap(document, [name]);
            //
            if (!lux.context.uiRouter)
                lux.loadRequire();
        }

        if (!angular_bootstrapped) {
            angular_bootstrapped = true;
            //
            $(document).ready(function() {
                _bootstrap();
            });
        }
    };
