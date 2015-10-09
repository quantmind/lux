
    // Controller for User.
    // This controller can be used by eny element, including forms
    angular.module('lux.users', ['lux.form', 'templates-users'])
        //
        // Directive for displaying page messages
        //
        //  <div data-options='sitemessages' data-page-messages></div>
        //  <script>
        //      sitemessages = {
        //          messages: [...],
        //          dismissUrl: (Optional url to use when dismissing a message)
        //      };
        //  </script>
        .directive('pageMessages', ['$lux', '$sce', function ($lux, $sce) {

            return {
                restrict: 'AE',
                templateUrl: "users/messages.tpl.html",
                scope: {},
                link: function (scope, element, attrs) {
                    scope.messageClass = {
                        info: 'alert-info',
                        success: 'alert-success',
                        warning: 'alert-warning',
                        danger: 'alert-danger',
                        error: 'alert-danger'
                    };
                    //
                    // Dismiss a message
                    scope.dismiss = function (e, m) {
                        var target = e.target;
                        while (target && target.tagName !== 'DIV')
                            target = target.parentNode;
                        $(target).remove();
                        $lux.post('/_dismiss_message', {message: m});
                    };
                    var messages = getOptions(attrs);
                    scope.messages = [];
                    forEach(messages, function (message) {
                        if (message) {
                            if (typeof(message) === 'string')
                                message = {body: message};
                            message.html = $sce.trustAsHtml(message.body);
                        }
                        scope.messages.push(message);
                    });
                }
            };
        }])

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
