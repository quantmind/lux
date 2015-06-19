
    //
    //	LUX API
    //	===================
    //
    //  Angular module for interacting with lux-based REST APIs
    angular.module('lux.webapi', ['lux.services'])

        .run(['$rootScope', '$lux', function ($scope, $lux) {
            //
            if ($scope.API_URL) {
                var api = $lux.api($scope.API_URL, luxweb);
                api.initScope($scope);
            }
        }]);


    var //
        //  HTTP verbs which don't send a csrf token in their requests
        CSRFset = ['get', 'head', 'options'],
        //
        luxweb = function (url, $lux) {

            var api = baseapi(url, $lux),
                request = api.request;

            // Set/Get the JWT token
            api.token = function (token) {
                var key = 'luxtoken-' + api.baseUrl();

                if (arguments.length) {
                    // Set the token
                    var decoded = lux.decodeJWToken(token);
                    if (decoded.storage === 'session')
                        sessionStorage.setItem(key, token);
                    else
                        localStorage.setItem(key, token);
                    return api;
                } else {
                    // Obtain the token
                    token = localStorage.getItem(key);
                    if (!token) token = sessionStorage.getItem(key);
                    return token;
                }
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

            // Perform Logout
            api.logout = function (scope) {
                scope.$emit('pre-logout');
                api.post({
                    name: 'authorizations_url',
                    path: '/logout'
                }).then(function () {
                    scope.$emit('after-logout');
                    $lux.window.reload();
                }, function (response) {
                    $lux.messages.error('Error while logging out');
                });
            };

            //
            //  Fired when a lux form uses this api to post data
            //
            //  Check the run method in the "lux.services" module for more information
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
            api.initScope = function (scope) {
                //  Get the api client
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
