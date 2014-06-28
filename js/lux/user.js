
    // Controller for User
    lux.controllers.controller('userController', ['$scope', '$element', '$location', '$http', '$sce',
            function ($scope, $element, $location, $http, $sce) {
        // Model for a user when updating
        formController($scope, $element, $location, $http, $sce);

        // Unlink account for a OAuth provider
        $scope.unlink = function(e, name) {
            e.preventDefault();
            e.stopPropagation();
            var url = '/oauth/' + name + '/remove';
            $.post(url).success(function (data) {
                if (data.success)
                    $route.reload();
            });
        };

        // Check if password is correct
        $scope.check_password_repeat = function () {
            var u = this.formModel,
                field = this.form.password_repeat,
                psw1 = u.password,
                psw2 = u.password_repeat;
            if (psw1 !== psw2 && field.$dirty) {
                this.formErrors.password_repeat = "passwords don't match";
                field.$error.password_repeat = true;
                this.formClasses.password_repeat = 'has-error';
            } else if (field.$dirty) {
                this.formClasses.password_repeat = 'has-success';
                delete this.form.$error.password_repeat;
            }
        };

    }]);