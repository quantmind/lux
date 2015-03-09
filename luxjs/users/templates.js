angular.module('templates-users', ['users/login-help.tpl.html', 'users/messages.tpl.html']);

angular.module("users/login-help.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("users/login-help.tpl.html",
    "<p class=\"text-center\">Don't have an account? <a ng-href=\"{{REGISTER_URL}}\" target=\"_self\">Create one</a></p>\n" +
    "<p class=\"text-center\">{{bla}}<a ng-href=\"{{RESET_PASSWORD_URL}}\" target=\"_self\">Forgot your username or password?</a></p>");
}]);

angular.module("users/messages.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("users/messages.tpl.html",
    "<div ng-repeat=\"message in messages\" class=\"alert alert-dismissible\"\n" +
    "ng-class=\"messageClass[message.level]\">\n" +
    "<button type=\"button\" class=\"close\" data-dismiss=\"alert\" ng-click=\"dismiss($event, message)\">\n" +
    "    <span aria-hidden=\"true\">&times;</span>\n" +
    "    <span class=\"sr-only\">Close</span>\n" +
    "</button>\n" +
    "<span ng-bind-html=\"message.html\"></span>\n" +
    "</div>");
}]);
