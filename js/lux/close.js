    //
    lux.bootstrap = function () {
        //
        $(document).ready(function() {
            //
            if (routes.length && context.html5mode) {
                var rs = routes;
                routes = [];
                lux._setupRouter(rs);
            }
            //
            angular.bootstrap(document, ['lux']);
            //
            angular.forEach(ready_callbacks, function (callback) {
                callback();
            });
            ready_callbacks = true;
        });
    };

	return lux;
});