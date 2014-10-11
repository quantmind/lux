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
            if (lux.context.uiRouter)
                modules.push('lux.ui.router');
            else
                modules.push('lux.router');
            // Add all modules from context
            forEach(lux.context.ngModules, function (mod) {
                modules.push(mod);
            });
            angular.module(name, modules);
            angular.bootstrap(document, [name]);
            //
            forEach(ready_callbacks, function (callback) {
                callback();
            });
            ready_callbacks = true;
        }

        if (!angular_bootstrapped) {
            angular_bootstrapped = true;
            //
            $(document).ready(function() {
                _bootstrap();
            });
        }
    };
