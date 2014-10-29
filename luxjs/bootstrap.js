    lux.loader = angular.module('lux.loader', []);

    lux.loader
        .value('context', lux.context)
        //
        .config(['$compileProvider', function (compiler) {
            lux.loader.directive = compiler.directive;
        }])
        //
        .run(['$rootScope', '$log', 'context', function (scope, log, context) {
            log.info('Extend root scope with context');
            extend(scope, context);
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
                modules.push('lux.ui.router');
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
