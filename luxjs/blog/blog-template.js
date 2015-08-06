angular.module('templates-blog', ['blog/templates/header.tpl.html', 'blog/templates/pagination.tpl.html']);

angular.module("blog/templates/header.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("blog/templates/header.tpl.html",
    "<h1 data-ng-bind=\"page.title\"></h1>\n" +
    "<p class=\"small\">by {{page.authors}} on {{page.dateText}}</p>\n" +
    "<p class=\"lead storyline\">{{page.description}}</p>\n" +
    "");
}]);

angular.module("blog/templates/pagination.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("blog/templates/pagination.tpl.html",
    "<ul class=\"media-list\">\n" +
    "    <li ng-repeat=\"post in items\" class=\"media\" data-ng-controller='BlogEntry'>\n" +
    "        <a href=\"{{post.html_url}}\" ng-attr-target=\"{{postTarget}}\">\n" +
    "            <div class=\"clearfix\">\n" +
    "                <img ng-src=\"{{post.image}}\" class=\"hidden-xs post-image\" alt=\"{{post.title}}\">\n" +
    "                <img ng-src=\"{{post.image}}\" alt=\"{{post.title}}\" class=\"visible-xs post-image-xs center-block\">\n" +
    "                <div class=\"post-body hidden-xs\">\n" +
    "                    <h3 class=\"media-heading\">{{post.title || \"Untitled\"}}</h3>\n" +
    "                    <p data-ng-if=\"post.description\">{{post.description}}</p>\n" +
    "                    <p class=\"text-info small\">by {{post.authors}} on {{post.dateText}}</p>\n" +
    "                </div>\n" +
    "                <div class=\"visible-xs\">\n" +
    "                    <br>\n" +
    "                    <h3 class=\"media-heading text-center\">{{post.title}}</h3>\n" +
    "                    <p data-ng-if=\"post.description\">{{post.description}}</p>\n" +
    "                    <p class=\"text-info small\">by {{post.authors}} on {{post.dateText}}</p>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "            <hr>\n" +
    "        </a>\n" +
    "    </li>\n" +
    "</ul>");
}]);
