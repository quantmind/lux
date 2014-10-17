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
    "        <a href=\"{{post.html_url}}\" class=\"pull-left hidden-xs dir-entry-image\">\n" +
    "          <img ng-src=\"{{post.image}}\" alt=\"{{post.title}}\">\n" +
    "        </a>\n" +
    "        <a href=\"{{post.html_url}}\" class=\"visible-xs\">\n" +
    "            <img ng-src=\"{{post.image}}\" alt=\"{{post.title}}\" class=\"dir-entry-image\">\n" +
    "        </a>\n" +
    "        <p class=\"visible-xs\"></p>\n" +
    "        <div class=\"media-body\">\n" +
    "            <h4 class=\"media-heading\"><a href=\"{{post.html_url}}\">{{post.title}}</a></h4>\n" +
    "            <p data-ng-if=\"post.description\">{{post.description}}</p>\n" +
    "            <p class=\"text-info small\">by {{post.authors}} on {{post.dateText}}</p>\n" +
    "        </div>\n" +
    "    </li>\n" +
    "</ul>");
}]);
