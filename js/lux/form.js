    var FORMKEY = 'm__form';
    //
    // add the watch change directive
    lux.app.directive('watchChange', function() {
        return {
            scope: {
                onchange: '&watchChange'
            },
            link: function(scope, element, attrs) {
                element.on('keyup', function() {
                    scope.$apply(function () {
                        scope.onchange();
                    });
                });
                element.on('change', function() {
                    scope.$apply(function () {
                        scope.onchange();
                    });
                });
            }
        };
    });

    // Change the form data depending on content type
    function formData(ct) {
        return function (data, getHeaders ) {
            if (ct === 'application/x-www-form-urlencoded')
                return $.param(options.data);
            else if (ct === 'multipart/form-data') {
                var fd = new FormData();
                angular.forEach(data, function (value, key) {
                    fd.append(key, value);
                });
                return fd;
            } else return data;
        };
    }

    function formController ($scope, $element, $location, $http, $sce, model) {
        model || (model = {});

        $scope.formModel = model;
        $scope.formClasses = {};
        $scope.formErrors = {};
        $scope.formMessages = {};

        $scope.checkField = function (name) {
            var checker = $scope['check_' + name];
            // There may be a custom field checker
            if (checker)
                checker.call($scope);
            else {
                var field = $scope.form[name];
                if (field.$valid)
                    $scope.formClasses[name] = 'has-success';
                else if (field.$dirty) {
                    $scope.formErrors[name] = name + ' is not valid';
                    $scope.formClasses[name] = 'has-error';
                }
            }
        };

        // display field errors
        $scope.showErrors = function () {
            var error = $scope.form.$error;
            angular.forEach(error.required, function (e) {
                $scope.formClasses[e.$name] = 'has-error';
            });
        };

        // process form
        $scope.processForm = function(e) {
            e.preventDefault();
            e.stopPropagation();
            //
            if ($scope.form.$invalid) {
                return $scope.showErrors();
            }

            var enctype = $element.attr('enctype') || '',
                ct = enctype.split(';')[0],
                options = {
                    url: $element.attr('action'),
                    method: $element.attr('method') || 'POST',
                    data: $scope.formModel,
                    transformRequest: formData(ct),
                };
            // Let the browser choose the content type
            if (ct === 'application/x-www-form-urlencoded' || ct === 'multipart/form-data') {
                options.headers = {
                    'content-type': undefined
                };
            }
            //
            $scope.formMessages = {};
            //
            // submit
            $http(options).success(function(data) {
                if (data.messages) {
                    angular.forEach(data.messages, function (messages, field) {
                        $scope.formMessages[field] = messages;
                    });
                } else {
                    window.location.href = data.redirect || '/';
                }
            }).error(function(data, status, headers, config) {
            });
        };
    }