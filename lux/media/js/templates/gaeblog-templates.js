angular.module('templates-gaeblog', ['templates/blog-actions.tpl.html', 'templates/blog-delete.tpl.html', 'templates/blog-page.tpl.html', 'templates/blog-publish.tpl.html', 'templates/blog-search.tpl.html', 'templates/modal.tpl.html']);

angular.module("templates/blog-actions.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/blog-actions.tpl.html",
    "<ul class=\"blogActions\" ng-class=\"layout\" ng-if=\"page\">\n" +
    "<li ng-if=\"page.id && !page.published\"><a class=\"btn btn-default\" ng-click=\"publishPost()\"> Publish</a></li>\n" +
    "<li ng-if=\"page.preview_url\"><a class=\"btn btn-default\" ng-href=\"{{page.preview_url}}\"> Preview</a></li>\n" +
    "<li ng-if=\"page.edit_url\"><a class=\"btn btn-default\" ng-href=\"{{page.edit_url}}\"> Write</a></li>\n" +
    "<li ng-if=\"page.id\"><a class=\"btn btn-danger\" ng-click=\"deletePost()\"> Delete</a></li>\n" +
    "</ul>");
}]);

angular.module("templates/blog-delete.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/blog-delete.tpl.html",
    "<div class=\"modal-body\">\n" +
    "    Deleted stories are gone forever. Are you sure?\n" +
    "</div>\n" +
    "<div class=\"modal-footer\">\n" +
    "  <button type=\"button\" class=\"btn btn-danger\" ng-click=\"deletePost(true)\">Delete</button>\n" +
    "  <button type=\"button\" class=\"btn btn-default\" ng-click=\"$hide()\">Cancel</button>\n" +
    "</div>");
}]);

angular.module("templates/blog-page.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/blog-page.tpl.html",
    "<div class=\"center-block blog-title w800\">\n" +
    "    <h2 data-ng-bind=\"page.title\"></h2>\n" +
    "    <p class=\"small\">by {{page.authors}} on {{page.dateText}}</p>\n" +
    "    <p class=\"lead storyline\">{{page.description}}</p>\n" +
    "</div>\n" +
    "<div class=\"center-block w900\">\n" +
    "    <br>\n" +
    "    <br>\n" +
    "    <section data-highlight data-compile-html>\n" +
    "    </section>\n" +
    "</div>");
}]);

angular.module("templates/blog-publish.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/blog-publish.tpl.html",
    "<div class=\"modal-body\">\n" +
    "    Do you want to publish your story?\n" +
    "</div>\n" +
    "<div class=\"modal-footer\">\n" +
    "  <button type=\"button\" class=\"btn btn-default\" ng-click=\"publishPost(true)\">Publish</button>\n" +
    "  <button type=\"button\" class=\"btn btn-default\" ng-click=\"$hide()\">Cancel</button>\n" +
    "</div>");
}]);

angular.module("templates/blog-search.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/blog-search.tpl.html",
    "<div class=\"searchBox\" ng-show=\"page.name == 'search'\">\n" +
    "<input class=\"borderless text-jumbo\" type=\"text\" placeholder=\"Type to search\" ng-change='change($event)' ng-model='text'>\n" +
    "<p class=\"lead text-center\" ng-if=\"message\" ng-bind=\"message\" style=\"margin-top: 20px\"></p>\n" +
    "</div>");
}]);

angular.module("templates/modal.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/modal.tpl.html",
    "<div class=\"modal\" tabindex=\"-1\" role=\"dialog\">\n" +
    "  <div class=\"modal-dialog\">\n" +
    "    <h3 class=\"opverlay-title\" ng-show=\"title\" ng-bind=\"title\"></h3>\n" +
    "    <div ng-bind=\"content\"></div>\n" +
    "  </div>\n" +
    "</div>");
}]);
