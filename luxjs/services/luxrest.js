    //
    //	Angular Module for JS clients of Lux Rest APIs
    //	====================================================
    //
    //	If the ``API_URL`` is defined at root scope, register the
    //	javascript client with the $lux service and add functions to the root
    //	scope to retrieve the api client handler and user informations
    angular.module('lux.restapi', ['lux.services'])

        .run(['$rootScope', '$window', '$lux', function (scope, $window, $lux) {

            // If the root scope has an API_URL register the luxrest client
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

    //
    //  API handler for lux rest api
    //
    //  This handler connects to lux-based rest apis and
    //
    //  * Perform authentication using username/email & password
    //  * After authentication a JWT is received and stored in the localStorage or sessionStorage
    //  * Optional second factor authentication
    //  --------------------------------------------------
    var luxrest = function (url, $lux) {

        var api = luxweb(url, $lux);

        api.httpOptions = function (request) {
            var options = request.options,
                headers = options.headers;
            if (!headers)
                options.headers = headers = {};
            headers['Content-Type'] = 'application/json';
        };

        // Set/Get the JWT token
        api.token = function (token) {
            var key = 'luxrest - ' + api.baseUrl();

            if (arguments.length) {
                var decoded = lux.decodeJWToken(token);
                if (decoded.storage === 'session')
                    sessionStorage.setItem(key, token);
                else
                    localStorage.setItem(key, token);
                return api;
            } else {
                token = localStorage.getItem(key);
                if (!token) token = sessionStorage.getItem(key);
                return token;
            }
        };

        api.logout = function () {
            var key = 'luxrest - ' + api.baseUrl();

            localStorage.removeItem(key);
            sessionStorage.removeItem(key);
        };

        api.user = function () {
            var token = api.token();
            if (token) {
                var u = lux.decodeJWToken(token);
                u.token = token;
                return u;
            }
        };

        // Add authentication token if available
        api.authentication = function (request) {
            //
            // If the call is for the authorizations_url api, add callback to store the token
            if (request.name === 'authorizations_url' &&
                    request.options.url === request.baseUrl &&
                    request.options.method === 'post') {

                request.on.success(function(data, status) {
                    api.token(data.token);
                });

            } else {
                var jwt = api.token();

                if (jwt) {
                    var headers = request.options.headers;
                    if (!headers)
                        request.options.headers = headers = {};

                    headers.Authorization = 'Bearer ' + jwt;
                }
            }
        };

        return api;
    };

