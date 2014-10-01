    //
    // Bootstrap the document
    lux.bootstrap = function (name, modules) {
        //
        // actual bootstrapping function
        function _bootstrap() {
            //
            // Resolve modules to load
            if (!$.isArray(modules))
                modules = [];
            modules.push('lux');
            // Add all modules from context
            forEach(context.ngModules, function (module) {
                modules.push(module);
            });
            luxAppModule(name, modules);
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
            //
            $(document).ready(function() {
                if (requires) {
                    require(requires, function () {
                        _bootstrap();
                    });
                } else {
                    _bootstrap();
                }
            });
        }
    };
