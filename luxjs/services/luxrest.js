    //
    // Add this module if the API_URL in the root scope is a lux-rest API
    angular.module('lux.restapi', ['lux.services'])

        .run(['$rootScope', '$lux', function (scope, $lux) {

            // If the scope has an API_URL register the client
            if (scope.API_URL)
            	$lux.api(scope.API_URL, luxrest);

        }]);

    function urlBase64Decode (str) {
        var output = str.replace('-', '+').replace('_', '/');
        switch (output.length % 4) {

            case 0: { break; }
        case 2: { output += '=='; break; }
        case 3: { output += '='; break; }
        default: {
                throw 'Illegal base64url string!';
            }
        }
        //polifyll https://github.com/davidchambers/Base64.js
        return decodeURIComponent(escape(window.atob(output)));
    }


    lux.decodeJWToken = function (token) {
        var parts = token.split('.');

        if (parts.length !== 3) {
            throw new Error('JWT must have 3 parts');
        }

        var decoded = urlBase64Decode(parts[1]);
        if (!decoded) {
            throw new Error('Cannot decode the token');
        }

        return JSON.parse(decoded);
    };
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
            options.url = request.baseUrl;
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

        // Add authentication token if available
		api.authentication = function (request) {
            //
            // If the call is for the authorizations_url api, add callback to store the token
            if (request.name === 'authorizations_url' &&
                    request.options.url === request.baseUrl &&
                    request.options.method === 'post')
                request.success(function(data, status) {
                    api.token(data.token);
                });
            else {
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
