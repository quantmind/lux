
    //
    //	LUX API
    //	===================
    //
    //  Angular module for interacting with lux-based REST APIs
    angular.module('lux.webapi', ['lux.services'])

        .run(['$rootScope', '$window', '$lux', function ($scope, $window, $lux) {
            //
            var name = $(document.querySelector("meta[name=csrf-param]")).attr('content'),
                csrf_token = $(document.querySelector("meta[name=csrf-token]")).attr('content');

            if (name && csrf_token) {
                $lux.csrf = {};
                $lux.csrf[name] = csrf_token;
            }

            if ($scope.API_URL) {

                $lux.api($scope.API_URL, luxweb);

                // logout via post method
                $scope.logout = function(e, url) {
                    e.preventDefault();
                    e.stopPropagation();
                    $lux.post(url).success(function (data) {
                        $window.location.reload();
                    });
                };
            }
        }]);


    var CSRFset = ['get', 'head', 'options'],
        //
        luxweb = function (url, $lux) {

        var api = baseapi(url, $lux),
            request = api.request;

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

        return api;
    };
