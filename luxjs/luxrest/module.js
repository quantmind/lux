    //
    // Add this module if the API_URL in the root scope is a lux-rest API
    angular.module('lux.restapi', ['lux.services'])

        .run(['$rootScope', '$window', '$lux', function (scope, $window, $lux) {

            // If the root scope has an API_URL register the client
            if (scope.API_URL) {

                $lux.api(scope.API_URL, luxrest);

                // Get the api client
                scope.api = function () {
                    return $lux.api(scope.API_URL);
                };

                // Get a user
                scope.getUser = function () {
                    var api = scope.api();
                    if (api)
                        return api.user();
                };

                scope.logout = function () {
                    var api = scope.api();
                    if (api && api.token()) {
                        api.logout();
                        $window.location.reload();
                    }
                };
            }

        }]);
