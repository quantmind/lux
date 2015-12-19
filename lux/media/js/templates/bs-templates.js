angular.module('templates-bs', ['bs/tooltip.tpl.html']);

angular.module("bs/tooltip.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("bs/tooltip.tpl.html",
    "<div class=\"tooltip in\" ng-show=\"title\">\n" +
    "    <div class=\"tooltip-arrow\"></div>\n" +
    "    <div class=\"tooltip-inner\" ng-bind=\"title\"></div>\n" +
    "</div>");
}]);
