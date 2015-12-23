define(['angular', 'lux'], function (angular, lux) {
    "use strict";

    angular.module('lux.form.handlers', ['lux.services'])

        .run(['$lux', function ($lux) {
            var formHandlers = {};
            $lux.formHandlers = formHandlers;

            formHandlers.reload = function () {
                $lux.window.location.reload();
            };

            formHandlers.redirectHome = function (response, scope) {
                var href = scope.formAttrs.redirectTo || '/';
                $lux.window.location.href = href;
            };

            // response handler for login form
            formHandlers.login = function (response, scope) {
                var target = scope.formAttrs.action,
                    api = $lux.api(target);
                if (api)
                    api.token(response.data.token);
                $lux.window.location.href = lux.context.POST_LOGIN_URL || lux.context.LOGIN_URL;
            };

            //
            formHandlers.passwordRecovery = function (response, scope) {
                var email = response.data.email;
                if (email) {
                    var text = "We have sent an email to <strong>" + email + "</strong>. Please follow the instructions to change your password.";
                    $lux.messages.success(text);
                }
                else
                    $lux.messages.error("Could not find that email");
            };

            //
            formHandlers.signUp = function (response, scope) {
                var email = response.data.email;
                if (email) {
                    var text = "We have sent an email to <strong>" + email + "</strong>. Please follow the instructions to confirm your email.";
                    $lux.messages.success(text);
                }
                else
                    $lux.messages.error("Something wrong, please contact the administrator");
            };

            //
            formHandlers.passwordChanged = function (response, scope) {
                if (response.data.success) {
                    var text = 'Password succesfully changed. You can now <a title="login" href="' + lux.context.LOGIN_URL + '">login</a> again.';
                    $lux.messages.success(text);
                } else
                    $lux.messages.error('Could not change password');
            };

            formHandlers.enquiry = function (response, scope) {
                if (response.data.success) {
                    var text = 'Thank you for your feedback!';
                    $lux.messages.success(text);
                } else
                    $lux.messages.error('Feedback form error');
            };

        }]);

});
