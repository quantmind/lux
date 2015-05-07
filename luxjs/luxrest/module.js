    //
    //	Angular Module for JS clients of Lux Rest APIs
    //	====================================================
    //
    //	If the ``API_URL`` is defined at root scope, register the
    //	javascript client with the $lux service and add functions to the root
    //	scope to retrieve the api client handler and user informations
    angular.module('lux.restapi', ['lux.services'])

        .run(['$rootScope', '$window', '$lux', function (scope, $window, $lux) {

            // If the root scope has an API_URL register the client
            if (scope.API_URL) {

                $lux.api(scope.API_URL, luxrest);

                //	Get the api client
                scope.api = function () {
                    return $lux.api(scope.API_URL);
                };

                // 	Get the current user
                scope.getUser = function () {
                    var api = scope.api();
                    if (api)
                        return api.user();
                };

                //	Logout the current user
                scope.logout = function () {
                    var api = scope.api();
                    if (api && api.token()) {
                        api.logout();
                        $window.location.reload();
                    }
                };
            }

        }]);
