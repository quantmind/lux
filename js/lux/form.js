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

    function formController ($scope, $element, $location, $http, model) {
        model || (model = {});

        $scope.formModel = model;
        $scope.formClasses = {};
        $scope.formErrors = {};

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
        };

        // process form
        $scope.processForm = function() {
            if ($scope.form.$invalid) {
                return $scope.showErrors();
            }

            var options = {
                url: $element.attr('action'),
                method: $element.attr('method') || 'POST',
                data: $scope.formModel
            };
            var enctype = $element.attr('enctype');
            if (enctype)
                options.headers = {
                    "Content-Type": enctype
                };
            // submit
            $http(options).success(function(data) {
                console.log(data);

                if (!data.success) {
                    // if not successful, bind errors to error variables
                    $scope.message = data.message;
                    if (data.errors) {
                        _(data.errors).forEach(function (obj) {
                            //$scope.errorName = data.errors.name;
                            //$scope.errorSuperhero = data.errors.superheroAlias;
                        });
                    } else if (data.html_url) {
                        window.location.href = data.html_url;
                    }
                } else {
                    // if successful, bind success message to message
                    $scope.message = data.message;
                }
            });
        };
    }