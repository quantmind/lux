    //
    //  API handler for lux web authentication
    //  ---------------------------------------
    angular.module('lux.web.api', ['lux.services'])

        .run(['$lux', function ($lux) {
            //
            var csrf = {},
                name = $(document.querySelector("meta[name=csrf-param]")).attr('content'),
                csrf_token = $(document.querySelector("meta[name=csrf-token]")).attr('content');

            if (name && csrf_token)
                csrf[name] = csrf_token;

            // A post method with CSRF parameter
            $lux.post = function (url, data, cfg) {
                var ct = cfg ? cfg.contentType : null,
                    fd = this.formData(ct);
                return this.http.post(url, fd(data), cfg);
            };

            //
            // Change the form data depending on content type
            $lux.formData = function (contentType) {

                return function (data) {
                    data = extend(data || {}, csrf);
                    if (contentType === 'application/x-www-form-urlencoded')
                        return $.param(data);
                    else if (contentType === 'multipart/form-data') {
                        var fd = new FormData();
                        forEach(data, function (value, key) {
                            fd.append(key, value);
                        });
                        return fd;
                    } else {
                        return data;
                    }
                };
            };
            //
            if (scope.API_URL)
                $lux.api(scope.API_URL, luxweb);
        }]);


    var luxweb = function (url, $lux) {

    	var api = baseapi(url, $lux);

    	api.authentication = function (request) {
            //
            if (lux.context.user_token) {
                self.auth = {user_token: lux.context.user_token};
            } else if (lux.context.user) {
                $lux.log.info('Fetching authentication token');
                //
                $lux.post('/_token').success(function (data) {
                    lux.context.user_token = data.token;
                    self.auth = {user_token: lux.context.user_token};
                    self.call(request);
                }).error(request.error);
                //
                return request.deferred.promise;
            } else {
                self.auth = {};
            }
            //
            // Add authentication token
            if (lux.context.user_token) {
                var headers = request.options.headers;
                if (!headers)
                    request.options.headers = headers = {};

                headers.Authorization = 'Bearer ' + lux.context.user_token;
            }
        };

        return api;
    };
