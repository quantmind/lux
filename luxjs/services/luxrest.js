    //
    //  API handler for lux rest api
	//
	//  This handler connects to lux-based rest apis and
	//
	//	* Perform authentication using username/email & password
	//	* After authentication a JWT is received and stored in the
	//	* Optional second factor authentication
    //  --------------------------------------------------
    angular.module('lux.restapi', ['lux.api'])

        .run(['$rootScope', '$lux', function (scope, $lux) {

            var key = 'luxrest',
                client;

            $lux.registerApi(key, {

            });

            scope.luxrest = function (url, options) {
                if (!arguments.length) return client;
                client = new ApiClient(key, url, options, $lux);
                return client;
            };

            if (scope.API_URL)
                scope.luxrest(scope.API_URL);
        }]);
