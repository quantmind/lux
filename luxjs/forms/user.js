
    // Controller for User.
    // This controller can be used by eny element, including forms
    angular.module('lux.users', ['lux.form'])
        //
        .directive('userForm', ['formRenderer', function (formRenderer) {
            //
            var directive = formRenderer.directive();
            //
            directive.controller = ['$scope', function (scope) {
                // Check if password is correct
                scope.check_password_repeat = function () {
                    var form = this[this.formName];
                    var field = this.form.password_repeat,
                        psw1 = form.password,
                        psw2 = form.password_repeat;
                    if (psw1 !== psw2 && field.$dirty) {
                        this.formErrors.password_repeat = "passwords don't match";
                        field.$error.password_repeat = true;
                        this.formClasses.password_repeat = 'has-error';
                    } else if (field.$dirty) {
                        this.formClasses.password_repeat = 'has-success';
                        delete this.form.$error.password_repeat;
                    }
                };
            }];

            return directive;
        }])

        .controller('UserController', ['$scope', '$lux', function (scope, lux) {
            // Model for a user when updating

            // Unlink account for a OAuth provider
            scope.unlink = function(e, name) {
                e.preventDefault();
                e.stopPropagation();
                var url = '/oauth/' + name + '/remove';
                $.post(url).success(function (data) {
                    if (data.success)
                        $route.reload();
                });
            };
        }]);