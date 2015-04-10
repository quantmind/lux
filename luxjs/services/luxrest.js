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

            // If the scope has an API_URL create the client
            if (scope.API_URL)
            	$lux.registerApi(API_URL, luxrest);

        }]);

    var luxrest = function (opts, $lux) {
    	
    	var api = luxapi(opts, $lux);
    	
		call: function (request) {
            var $lux = this.$lux,
                url = request.options.url || this._url;

            if (this.apiUrls) {
            	this._url = url = this.apiUrls[this.name];
                    //
                    // No api url!
                    if (url)
                        return request.error('Could not find a valid url for ' + this.name);
                    //
                } else if (lux.context.apiUrl) {
                    // Fetch the api urls
                    var self = this;
                    $lux.log.info('Fetching api info');
                    return $lux.http.get(lux.context.apiUrl).success(function (resp) {
                        self.apiUrls = resp;
                        self.call(request);
                    }).error(request.error);
                    //
                } else
                    return request.error('Api url not available');
            }
            //
            // Fetch authentication token?
            if (!this.auth)
                return this.authentication(request);
            //
            // Add authentication
            this.addAuth(request);
            //
            var options = this.httpOptions(request);
            //
            if (options.url) {
                $lux.log.info('Executing HTTP ' + options.method + ' request @ ' + options.url);
                $lux.http(options).success(request.success).error(request.error);
            }
            else
                request.error('Api url not available');
        }
    };
