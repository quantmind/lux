    //
    // Bootstrap the document
    lux.bootstrap = function () {
        //
        function setup_angular(modules) {
            //
            if (!$.isArray(modules))
                modules = [];
            modules.push('lux');
            forEach(context.ngModules, function (module) {
                modules.push(module);
            });
            //
            angular.bootstrap(document, modules);
            //
            forEach(ready_callbacks, function (callback) {
                callback();
            });
            ready_callbacks = true;
        }
        //
        $(document).ready(function() {
            //
            if (context.html5mode) {
                //
                // Load angular-route and configure the HTML5 navigation
                require(['angular-route'], function () {
                    //
                    if (routes.length) {
                        var all = routes;
                        routes = [];
                        //
                        lux.app.config(['$routeProvider', '$locationProvider',
                                function($routeProvider, $locationProvider) {
                            //
                            angular.forEach(all, function (route) {
                                var url = route[0];
                                var data = route[1];
                                if ($.isFunction(data)) data = data();
                                $routeProvider.when(url, data);
                            });
                            // use the HTML5 History API
                            $locationProvider.html5Mode(true);
                        }]);
                    }
                    setup_angular();
                });
            } else {
                setup_angular();
            }
        });
    };

