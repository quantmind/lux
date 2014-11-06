angular.module('templates-blog', ['blog/header.tpl.html', 'blog/pagination.tpl.html']);

angular.module("blog/header.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("blog/header.tpl.html",
    "<h2 data-ng-bind=\"page.title\"></h2>\n" +
    "<p class=\"small\">by {{page.authors}} on {{page.dateText}}</p>\n" +
    "<p class=\"lead storyline\">{{page.description}}</p>");
}]);

angular.module("blog/pagination.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("blog/pagination.tpl.html",
    "<ul class=\"media-list\">\n" +
    "    <li ng-repeat=\"post in items\" class=\"media\" data-ng-controller='BlogEntry'>\n" +
    "        <a href=\"{{post.html_url}}\">\n" +
    "            <img ng-src=\"{{post.image}}\" class=\"hidden-xs post-image\" alt=\"{{post.title}}\">\n" +
    "            <img ng-src=\"{{post.image}}\" alt=\"{{post.title}}\" class=\"visible-xs post-image-xs center-block\">\n" +
    "            <div class=\"post-body hidden-xs\">\n" +
    "                <h3 class=\"media-heading\">{{post.title}}</h3>\n" +
    "                <p data-ng-if=\"post.description\">{{post.description}}</p>\n" +
    "                <p class=\"text-info small\">by {{post.authors}} on {{post.dateText}}</p>\n" +
    "            </div>\n" +
    "            <div class=\"visible-xs\">\n" +
    "                <br>\n" +
    "                <h3 class=\"media-heading text-center\">{{post.title}}</h3>\n" +
    "                <p data-ng-if=\"post.description\">{{post.description}}</p>\n" +
    "                <p class=\"text-info small\">by {{post.authors}} on {{post.dateText}}</p>\n" +
    "            </div>\n" +
    "        </a>\n" +
    "        <hr>\n" +
    "    </li>\n" +
    "</ul>");
}]);
