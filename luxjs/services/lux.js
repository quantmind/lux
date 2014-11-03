    //
    //  Lux web and api handler
    //  ----------------------
    angular.module('lux.web.api', ['lux.api'])

        .run(['$lux', function ($lux) {
            //
            var csrf = {},
                name = $(document.querySelector("meta[name=csrf-param]")).attr('content'),
                token = $(document.querySelector("meta[name=csrf-token]")).attr('content');

            if (name && token)
                csrf[name] = token;

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
            $lux.registerApi('lux', {
                //
                authentication: function (request) {
                    var self = this;
                    //
                    if (lux.context.user) {
                        $lux.log.info('Fetching authentication token');
                        //
                        $lux.post('/_token').success(function (data) {
                            self.auth = {user_token: data.token};
                            self.call(request);
                        }).error(request.error);
                        //
                        return request.deferred.promise;
                    } else {
                        self.auth = {};
                        self.call(request);
                    }
                },
                //
                addAuth: function (api, options) {
                    //
                            // Add authentication token
                    if (this.user_token) {
                        var headers = options.headers;
                        if (!headers)
                            options.headers = headers = {};

                        headers.Authorization = 'Bearer ' + this.user_token;
                    }
                },
            });
        }]);
