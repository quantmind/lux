angular.module('templates-page', ['lux/page/breadcrumbs.tpl.html']);

angular.module("lux/page/breadcrumbs.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("lux/page/breadcrumbs.tpl.html",
    "<ol class=\"breadcrumb\">\n" +
    "    <li ng-repeat=\"step in steps\" ng-class=\"{active: step.last}\">\n" +
    "        <a ng-if=\"!step.last\" href=\"{{step.href}}\">{{step.label}}</a>\n" +
    "        <span ng-if=\"step.last\">{{step.label}}</span>\n" +
    "    </li>\n" +
    "</ol>");
}]);
