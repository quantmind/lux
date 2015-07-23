angular.module('templates-cms', ['cms/templates/list-group.tpl.html']);

angular.module("cms/templates/list-group.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("cms/templates/list-group.tpl.html",
    "<div class=\"list-group\">\n" +
    "  <a ng-repeat=\"link in links\" ng-href=\"{{link.url}}\" class=\"list-group-item\" ng-bind=\"link.title\"></a>\n" +
    "</div>");
}]);
