define(['angular',
        'lux/main'], function (angular, lux) {
    'use strict';
    //
    //	LUX WEB API
    //	===================
    //
    //  Angular module for interacting with lux-based WEB APIs
    angular.module('lux.webapi', ['lux.services'])

        .run(['$rootScope', '$lux', function ($scope, $lux) {
            //
            if ($scope.API_URL) {
                $lux.api($scope.API_URL, luxweb).scopeApi($scope);
            }
        }]);

    //
    //	Decode JWT
    //	================
    //
    //	Decode a JASON Web Token and return the decoded object
    lux.decodeJWToken = function (token) {
        var parts = token.split('.');

        if (parts.length !== 3) {
            throw new Error('JWT must have 3 parts');
        }

        return lux.urlBase64DecodeToJSON(parts[1]);
    };

    var //
        //  HTTP verbs which don't send a csrf token in their requests
        CSRFset = ['get', 'head', 'options'],
        //
        luxweb = function (url, $lux) {

            var api = lux.apiFactory(url, $lux),
                request = api.request,
                auth_name = 'authorizations_url';

            // Set the name of the authentication endpoints
            api.authName = function (name) {
                if (arguments.length === 1) {
                    auth_name = name;
                    return api;
                } else
                    return auth_name;
            };

            // Set/Get the user token
            api.token = function () {
                return $lux.user_token;
            };

            // Perform Logout
            api.logout = function (scope) {
                var auth = $lux.authApi(api);
                if (!auth) {
                    $lux.messages.error('Error while logging out');
                    return;
                }
                scope.$emit('pre-logout');
                auth.post({
                    name: auth.authName(),
                    path: lux.context.LOGOUT_URL
                }).then(function () {
                    scope.$emit('after-logout');
                    if (lux.context.POST_LOGOUT_URL) {
                        $lux.window.location.href = lux.context.POST_LOGOUT_URL;
                    } else {
                        $lux.window.location.reload();
                    }
                }, function () {
                    $lux.messages.error('Error while logging out');
                });
            };

            // Get the user from the JWT
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
                if (lux.context.LOGIN_URL) {
                    $lux.window.location.href = lux.context.LOGIN_URL;
                    $lux.window.reload();
                }
            };

            //
            //  Fired when a lux form uses this api to post data
            //
            //  Check the run method in the "lux.services" module for more information
            api.formReady = function (model, formScope) {
                var resolve = api.defaults().get;
                if (resolve) {
                    api.get().success(function (data) {
                        lux.forEach(data, function (value, key) {
                            // TODO: do we need a callback for JSON fields?
                            // or shall we leave it here?

                            var modelType = formScope[formScope.formModelName + 'Type'];
                            var jsonArrayKey = key.split('[]')[0];

                            // Stringify json only if has json mode enabled
                            if (modelType[jsonArrayKey] === 'json' && lux.isJsonStringify(value)) {

                                // Get rid of the brackets from the json array field
                                if (angular.isArray(value)) {
                                    key = jsonArrayKey;
                                }

                                value = angular.toJson(value, null, 4);
                            }

                            if (angular.isArray(value)) {
                                model[key] = [];
                                angular.forEach(value, function (item) {
                                    model[key].push(item.id || item);
                                });
                            } else {
                                model[key] = value.id || value;
                            }
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
                    else if (status === 404)
                        $lux.log.info('Endpoint not found' + ((opts.path) ? ' @ ' + opts.path : ''));
                });
                return promise;
            };

            api.httpOptions = function (request) {
                var options = request.options;

                if ($lux.csrf && CSRFset.indexOf(options.method === -1)) {
                    options.data = angular.extend(options.data || {}, $lux.csrf);
                }

                if (!options.headers)
                    options.headers = {};
                options.headers['Content-Type'] = 'application/json';
            };

            //
            // Initialise a scope with an auth api handler
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
                    if (api.user()) api.logout(scope);
                };
            };

            return api;
        };

    return luxweb;
});
