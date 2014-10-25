
    // Controller for User.
    // This controller can be used by eny element, including forms
    angular.module('lux.users', ['lux.form'])

        .directive('userForm', ['formRenderer', function (renderer) {
            //
            renderer._createElement = renderer.createElement;

            // Override createElement to add passwordVerify directive in the password_repead input
            renderer.createElement = function (scope) {

                var element = this._createElement(scope),
                    field = scope.field,
                    other = field['data-check-repeat'] || field['check-repeat'];

                if (other) {
                    var msg = field.errorMessage || (other + " doesn't match"),
                        errors = $(element[0].querySelector('.' + scope.formErrorClass));
                    if (errors.length)
                        errors.html('').append(renderer[field.layout].fieldErrorElement(
                            scope, '$error.repeat', msg));
                }
                return element;
            };

            return renderer.directive();
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