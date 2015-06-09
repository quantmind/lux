
    //
    //	LUX API
    //	===================
    //
    //  Angular module for interacting with lux-based REST APIs
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
            if (scope.API_URL) {

                $lux.api(scope.API_URL, luxweb);

                // logout via post method
                scope.logout = function(e, url) {
                    e.preventDefault();
                    e.stopPropagation();
                    $lux.post(url).success(function (data) {
                        if (data.redirect)
                            window.location.replace(data.redirect);
                    });
                };
            }
        }]);


    var luxweb = function (url, $lux) {

        var api = baseapi(url, $lux),
            request = api.request;

        // Redirect to the LOGIN_URL
        api.login = function () {
            $lux.window.location.href = lux.context.LOGIN_URL;
            $lux.window.reload();
        };

        //
        //  Fired when a lux form uses this api to post data
        //  Check the run method in the "lux.services" module for more info
        api.formReady = function (model, formScope) {
            var id = api.defaults().id;
            if (id) {
                api.get({path: '/' + id}).success(function (data) {
                    angular.extend(form, data);
                });
            }
        };

        //  override request and attach error callbacks
        api.request = function (method, opts, data) {
            var promise = request.call(api, method, opts, data);
            promise.error(function (data, status) {
                if (status === 401)
                    api.login();
                else if (!status)
                    $lux.log.error('Server down, could not complete request');
                else if (status === 404) {
                    $lux.window.location.href = '/';
                    $lux.window.reload();
                }
            });
            return promise;
        };

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
