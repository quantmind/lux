angular.module('templates-sidebar', ['sidebar/nav-link.tpl.html', 'sidebar/sidebar.tpl.html']);

angular.module("sidebar/nav-link.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("sidebar/nav-link.tpl.html",
    "<a ng-attr-title=\"link.title\" ng-class=\"link.klass\" ng-click=\"clickLink($event, link)\"\n" +
    "ng-href=\"{{link.href}}\" data-title=\"{{link.title}}\"\n" +
    "ng-attr-target=\"{{link.target}}\">\n" +
    "<i ng-if=\"link.icon\" class=\"{{link.icon}}\"></i>\n" +
    "<span ng-if=\"!link.image\">{{link.label || link.name}}</span>\n" +
    "<img ng-if=\"link.image\" src=\"{{link.image}}\"/>\n" +
    "</a>\n" +
    "\n" +
    "<ul class=\"treeview-menu\" ng-class=\"link.class\" ng-if=\"link.subitems\">\n" +
    "    <li ng-repeat=\"link in link.subitems\" ng-class=\"{active:activeLink(link)}\" ng-include='sidebar/nav-link.tpl.html'></li>\n" +
    "</ul>\n" +
    "");
}]);

angular.module("sidebar/sidebar.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("sidebar/sidebar.tpl.html",
    "<nav ng-attr-id=\"{{sidebar.navbar.id}}\" class=\"navbar navbar-{{sidebar.navbar.themeTop}}\"\n" +
    "ng-class=\"{'navbar-fixed-top':sidebar.navbar.fixed, 'navbar-static-top':sidebar.navbar.top}\" role=\"navigation\"\n" +
    "ng-model=\"sidebar.navbar.collapse\" bs-collapse>\n" +
    "    <div class=\"{{sidebar.navbar.container}}\">\n" +
    "        <div class=\"navbar-header\">\n" +
    "            <button ng-if=\"sidebar.navbar.toggle\" type=\"button\" class=\"navbar-toggle\" bs-collapse-toggle>\n" +
    "                <span class=\"sr-only\">Toggle sidebar</span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "            </button>\n" +
    "            <a ng-if=\"sidebar.navbar.brandImage\" href=\"{{sidebar.navbar.url}}\" class=\"navbar-brand\" target=\"{{sidebar.navbar.target}}\">\n" +
    "                <img ng-src=\"{{sidebar.navbar.brandImage}}\" alt=\"{{sidebar.navbar.brand || 'brand'}}\">\n" +
    "            </a>\n" +
    "            <a ng-if=\"!sidebar.navbar.brandImage && sidebar.navbar.brand\" href=\"{{sidebar.navbar.url}}\" class=\"navbar-brand\" target=\"{{sidebar.navbar.target}}\">\n" +
    "                {{sidebar.navbar.brand}}\n" +
    "            </a>\n" +
    "        </div>\n" +
    "        <div>\n" +
    "            <ul ng-if=\"sidebar.navbar.items\" class=\"nav navbar-nav navbar-main\">\n" +
    "                <li ng-repeat=\"link in sidebar.navbar.items\" ng-class=\"{active:activeLink(link)}\" nav-sidebar-link>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "        </div>\n" +
    "        <div class=\"navbar-collapse\" bs-collapse-target>\n" +
    "            <ul ng-if=\"sidebar.navbar.itemsRight\" class=\"nav navbar-nav navbar-side\" >\n" +
    "                <li ng-repeat=\"link in sidebar.navbar.itemsRight\" ng-class=\"{active:activeLink(link)}\" nav-sidebar-link>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</nav>\n" +
    "\n" +
    "<aside ng-if=\"user\" ng-attr-id=\"{{sidebar.id}}\" class=\"main-sidebar\"\n" +
    "       ng-class=\"{'sidebar-fixed':sidebar.fixed}\">\n" +
    "    <section ng-if=\"sidebar.sections\" class=\"sidebar\">\n" +
    "        <div class=\"user-panel\">\n" +
    "            <div ng-if=\"user.avatar\" class=\"pull-left image\">\n" +
    "                <img src=\"{{user.avatar}}\" alt=\"User Image\" />\n" +
    "            </div>\n" +
    "            <div class=\"pull-left info\">\n" +
    "                <p>SIGNED IN AS</p>\n" +
    "                <a href=\"#\">{{user.name}}</a>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "        <ul class=\"sidebar-menu\">\n" +
    "            <li ng-if=\"section.name\" ng-repeat-start=\"section in sidebar.sections\" class=\"header\">\n" +
    "                {{section.name}}\n" +
    "            </li>\n" +
    "            <li ng-repeat-end ng-repeat=\"link in section.items\" class=\"treeview\"\n" +
    "            ng-class=\"{active:activeLink(link)}\" ng-include=\"'subnav'\"></li>\n" +
    "        </ul>\n" +
    "    </section>\n" +
    "</aside>\n" +
    "\n" +
    "\n" +
    "<script type=\"text/ng-template\" id=\"subnav\">\n" +
    "    <a ng-href=\"{{link.href}}\" ng-attr-title=\"{{link.title}}\" ng-click=\"menuCollapse($event)\">\n" +
    "        <i ng-if=\"link.icon\" class=\"{{link.icon}}\"></i>\n" +
    "        <span>{{link.name}}</span>\n" +
    "        <i ng-if=\"link.subitems\" class=\"fa fa-angle-left pull-right\"></i>\n" +
    "    </a>\n" +
    "    <ul class=\"treeview-menu\" ng-class=\"link.class\" ng-if=\"link.subitems\">\n" +
    "        <li ng-repeat=\"link in link.subitems\" ng-class=\"{active:activeLink(link)}\" ng-include=\"'subnav'\"></li>\n" +
    "    </ul>\n" +
    "</script>\n" +
    "");
}]);
