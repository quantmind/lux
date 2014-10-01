angular.module('templates-blog', ['lux/blog/header.tpl.html', 'lux/blog/pagination.tpl.html']);

angular.module("lux/blog/header.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("lux/blog/header.tpl.html",
    "<h2 data-ng-bind=\"page.title\"></h2>\n" +
    "<p class=\"small\">by {{page.authors}} on {{page.dateText}}</p>\n" +
    "<p class=\"lead storyline\">{{page.description}}</p>");
}]);

angular.module("lux/blog/pagination.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("lux/blog/pagination.tpl.html",
    "<ul class=\"media-list\">\n" +
    "    <li ng-repeat=\"post in items\" class=\"media\" data-ng-controller='BlogEntry'>\n" +
    "        <a href=\"{{post.html_url}}\" class=\"pull-left hidden-xs dir-entry-image\">\n" +
    "          <img data-ng-if=\"post.image\" src=\"{{post.image}}\" alt=\"{{post.title}}\">\n" +
    "          <img data-ng-if=\"!post.image\" src=\"holder.js/120x90\">\n" +
    "        </a>\n" +
    "        <a href=\"{{post.html_url}}\" class=\"visible-xs\">\n" +
    "            <img data-ng-if=\"post.image\" src=\"{{post.image}}\" alt=\"{{post.title}}\" class=\"dir-entry-image\">\n" +
    "            <img data-ng-if=\"!post.image\" src=\"holder.js/120x90\">\n" +
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
