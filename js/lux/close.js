    //
    lux.bootstrap = function () {
        //
        function setup_angular() {
            //
            $.each(context.ngModules, function (i, module) {
                if (lux.app.requires.indexOf(module) === -1)
                    lux.app.requires.push(module);
            });
            //
            angular.bootstrap(document, ['lux']);
            //
            angular.forEach(ready_callbacks, function (callback) {
                callback();
            });
            ready_callbacks = true;
        }
        //
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

	return lux;
});