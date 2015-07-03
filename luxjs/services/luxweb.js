
    //
    //	LUX API
    //	===================
    //
    //  Angular module for interacting with lux-based REST APIs
    angular.module('lux.webapi', ['lux.services'])

        .run(['$rootScope', '$lux', function ($scope, $lux) {
            //
            if ($scope.API_URL) {
                $lux.api($scope.API_URL, luxweb).scopeApi($scope);
            }
        }]);


    var //
        //  HTTP verbs which don't send a csrf token in their requests
        CSRFset = ['get', 'head', 'options'],
        //
        luxweb = function (url, $lux) {

            var api = baseapi(url, $lux),
                request = api.request,
                auth_name = 'authorizations_url',
                web;

            // Set the name of the authentication endpoints
            api.authName = function (name) {
                if (arguments.length === 1) {
                    auth_name = name;
                    return api;
                } else
                    return auth_name;
            };

            // Set/Get the JWT token
            api.token = function (token) {
                var auth = $lux.authApi(api);
                if (auth) return auth.token();

                var key = 'luxtoken-' + api.baseUrl();

                if (arguments.length) {
                    if (token) {
                        // Set the token
                        var decoded = lux.decodeJWToken(token);
                        if (decoded.storage === 'session')
                            sessionStorage.setItem(key, token);
                        else
                            localStorage.setItem(key, token);
                    } else {
                        sessionStorage.removeItem(key);
                        localStorage.removeItem(key);
                    }
                    return api;
                } else {
                    // Obtain the token
                    token = localStorage.getItem(key);
                    if (!token) token = sessionStorage.getItem(key);
                    return token;
                }
            };

            // Perform Logout
            api.logout = function (scope) {
                var auth = $lux.authApi(api);
                if (auth) return auth.logout(scope);

                scope.$emit('pre-logout');
                api.post({
                    name: api.authName(),
                    path: '/logout'
                }).then(function () {
                    scope.$emit('after-logout');
                    api.token(undefined);
                    $lux.window.location.reload();
                }, function (response) {
                    $lux.messages.error('Error while logging out');
                });
            };

            // Get the user fro the JWT
            api.user = function () {
                var token = api.token();
                if (token) {
                    var u = lux.decodeJWToken(token);
                    u.token = token;
                    return u;
                }
            };

            // Redirect to the LOGIN_URL
            api.login = function () {
                $lux.window.location.href = lux.context.LOGIN_URL;
                $lux.window.reload();
            };

            //
            //  Fired when a lux form uses this api to post data
            //
            //  Check the run method in the "lux.services" module for more information
            api.formReady = function (model, formScope) {
                var resolve = api.defaults().get;
                if (resolve) {
                    api.get().success(function (data) {
                        forEach(data, function (value, key) {
                            // TODO: do we need a callback for JSON fields?
                            // or shall we leave it here?
                            if (isObject(value)) value = JSON.stringify(value, null, 4);
                            model[key] = value;
                        });
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

            api.httpOptions = function (request) {
                var options = request.options;

                if ($lux.csrf && CSRFset.indexOf(options.method === -1)) {
                    options.data = extend(options.data || {}, $lux.csrf);
                }

                if (!options.headers)
                    options.headers = {};
                options.headers['Content-Type'] = 'application/json';
            };

            //
            // Initialise a scope with this api
            api.scopeApi = function (scope, auth) {
                //  Get the api client
                if (auth) {
                    // Register auth as the authentication client of this api
                    $lux.authApi(api, auth);
                    auth.authName(null);
                }

                scope.api = function () {
                    return $lux.api(url);
                };

                //  Get the current user
                scope.getUser = function () {
                    return api.user();
                };

                //  Logout the current user
                scope.logout = function (e) {
                    if (e && e.preventDefault) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                    if (api.user()) {
                        api.logout(scope);
                    }
                };
            };

            return api;
        };
