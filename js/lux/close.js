
    //
    // Load angular
    angular.element(document).ready(function() {
        //
        if (routes.length && context.html5) {
            var rs = routes;
            routes = [];
            lux._setupRouter(rs);
        }
        angular.bootstrap(document, ['lux']);
        //
        var callbacks = lux.ready_callbacks;
        lux.ready_callbacks = [];
        angular.forEach(callbacks, function (callback) {
            callback();
        });
    });

	return lux;
});