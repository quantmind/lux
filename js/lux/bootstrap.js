    //
    // Bootstrap the document
    lux.bootstrap = function (modules) {
        //
        // actual bootstrapping function
        function doit() {
            //
            // Resolve modules to load
            if (!$.isArray(modules))
                modules = [];
            modules.push('lux');
            forEach(context.ngModules, function (module) {
                modules.push(module);
            });
            //
            // routes available, setup router
            if (routes.length)
                setup_routes(routes);
            //
            angular.bootstrap(document, modules);
            //
            forEach(ready_callbacks, function (callback) {
                callback();
            });
            ready_callbacks = true;
        }
        //
        function setup_routes (all) {
            var routes = [];
                //
                angular.module('lux')
                    .config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
                        // setup
                        $stateProvider.html5Mode(true);
                    //
                    //angular.forEach(all, function (route) {
                    //    var url = route[0];
                    //    var data = route[1];
                    //    if ($.isFunction(data)) data = data();
                    //    $routeProvider.when(url, data);
                    //});
                    // use the HTML5 History API
                    //$locationProvider.html5Mode(true);
                }]);
        }
        //
        //
        $(document).ready(function() {
            if (requires) {
                require(requires, function () {
                    doit();
                });
            } else {
                doit();
            }
        });
    };

