angular.module('templates-page', ['page/breadcrumbs.tpl.html', 'page/messages.tpl.html']);

angular.module("page/breadcrumbs.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("page/breadcrumbs.tpl.html",
    "<ol class=\"breadcrumb\">\n" +
    "    <li ng-repeat=\"step in steps\" ng-class=\"{active: step.last}\">\n" +
    "        <a ng-if=\"!step.last\" href=\"{{step.href}}\">{{step.label}}</a>\n" +
    "        <span ng-if=\"step.last\">{{step.label}}</span>\n" +
    "    </li>\n" +
    "</ol>");
}]);

angular.module("page/messages.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("page/messages.tpl.html",
    "<div ng-repeat=\"message in messages\" class=\"alert alert-dismissible\"\n" +
    "ng-class=\"messageClass[message.level]\">\n" +
    "<button type=\"button\" class=\"close\" data-dismiss=\"alert\" ng-click=\"dismiss($event, message)\">\n" +
    "    <span aria-hidden=\"true\">&times;</span>\n" +
    "    <span class=\"sr-only\">Close</span>\n" +
    "</button>\n" +
    "<span ng-bind-html=\"message.body\"></span>\n" +
    "</div>");
}]);
