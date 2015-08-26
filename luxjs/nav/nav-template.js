angular.module('templates-nav', ['nav/templates/link.tpl.html', 'nav/templates/navbar.tpl.html', 'nav/templates/navbar2.tpl.html', 'nav/templates/sidebar.tpl.html']);

angular.module("nav/templates/link.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("nav/templates/link.tpl.html",
    "<a ng-if=\"link.title\" ng-href=\"{{link.href}}\" title=\"{{link.title}}\" ng-click=\"clickLink($event, link)\"\n" +
    "ng-attr-target=\"{{link.target}}\" ng-class=\"link.klass\" bs-tooltip=\"tooltip\">\n" +
    "<span ng-if=\"link.left\" class=\"left-divider\"></span>\n" +
    "<i ng-if=\"link.icon\" class=\"{{link.icon}}\"></i>\n" +
    "<span>{{link.label || link.name}}</span>\n" +
    "<span ng-if=\"link.right\" class=\"right-divider\"></span></a>\n" +
    "<a ng-if=\"!link.title\" ng-href=\"{{link.href}}\" title=\"{{link.title}}\" ng-click=\"clickLink($event, link)\"\n" +
    "ng-attr-target=\"{{link.target}}\" ng-class=\"link.klass\" bs-tooltip=\"tooltip\">\n" +
    "<span ng-if=\"link.left\" class=\"left-divider\"></span>\n" +
    "<i ng-if=\"link.icon\" class=\"{{link.icon}}\"></i>\n" +
    "<span>{{link.label || link.name}}</span>\n" +
    "<span ng-if=\"link.right\" class=\"right-divider\"></span></a>");
}]);

angular.module("nav/templates/navbar.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("nav/templates/navbar.tpl.html",
    "<nav ng-attr-id=\"{{navbar.id}}\" class=\"navbar navbar-{{navbar.themeTop}}\"\n" +
    "ng-class=\"{'navbar-fixed-top':navbar.fixed, 'navbar-static-top':navbar.top}\" role=\"navigation\"\n" +
    "ng-model=\"navbar.collapse\" bs-collapse>\n" +
    "    <div class=\"{{navbar.container}}\">\n" +
    "        <div class=\"navbar-header\">\n" +
    "            <button ng-if=\"navbar.toggle\" type=\"button\" class=\"navbar-toggle\" bs-collapse-toggle>\n" +
    "                <span class=\"sr-only\">Toggle navigation</span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "            </button>\n" +
    "            <ul class=\"nav navbar-nav main-nav\">\n" +
    "                <li ng-if=\"navbar.itemsLeft\" ng-repeat=\"link in navbar.itemsLeft\" ng-class=\"{active:activeLink(link)}\" navbar-link>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "            <a ng-if=\"navbar.brandImage\" href=\"{{navbar.url}}\" class=\"navbar-brand\" target=\"{{navbar.target}}\">\n" +
    "                <img ng-src=\"{{navbar.brandImage}}\" alt=\"{{navbar.brand || 'brand'}}\">\n" +
    "            </a>\n" +
    "            <a ng-if=\"!navbar.brandImage && navbar.brand\" href=\"{{navbar.url}}\" class=\"navbar-brand\" target=\"{{navbar.target}}\">\n" +
    "                {{navbar.brand}}\n" +
    "            </a>\n" +
    "        </div>\n" +
    "        <nav class=\"navbar-collapse\" bs-collapse-target>\n" +
    "            <ul ng-if=\"navbar.itemsRight\" class=\"nav navbar-nav navbar-right\">\n" +
    "                <li ng-repeat=\"link in navbar.itemsRight\" ng-class=\"{active:activeLink(link)}\" navbar-link>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "        </nav>\n" +
    "    </div>\n" +
    "</nav>\n" +
    "");
}]);

angular.module("nav/templates/navbar2.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("nav/templates/navbar2.tpl.html",
    "<nav class=\"navbar navbar-{{navbar.themeTop}}\"\n" +
    "ng-class=\"{'navbar-fixed-top':navbar.fixed, 'navbar-static-top':navbar.top}\"\n" +
    "role=\"navigation\" ng-model=\"navbar.collapse\" bs-collapse>\n" +
    "    <div class=\"navbar-header\">\n" +
    "        <button ng-if=\"navbar.toggle\" type=\"button\" class=\"navbar-toggle\" bs-collapse-toggle>\n" +
    "            <span class=\"sr-only\">Toggle navigation</span>\n" +
    "            <span class=\"icon-bar\"></span>\n" +
    "            <span class=\"icon-bar\"></span>\n" +
    "            <span class=\"icon-bar\"></span>\n" +
    "        </button>\n" +
    "        <a ng-if=\"navbar.brandImage\" href=\"{{navbar.url}}\" class=\"navbar-brand\" target=\"{{navbar.target}}\">\n" +
    "            <img ng-src=\"{{navbar.brandImage}}\" alt=\"{{navbar.brand || 'brand'}}\">\n" +
    "        </a>\n" +
    "        <a ng-if=\"!navbar.brandImage && navbar.brand\" href=\"{{navbar.url}}\" class=\"navbar-brand\" target=\"{{navbar.target}}\">\n" +
    "            {{navbar.brand}}\n" +
    "        </a>\n" +
    "    </div>\n" +
    "    <ul ng-if=\"navbar.items\" class=\"nav navbar-nav\">\n" +
    "        <li ng-repeat=\"link in navbar.items\" ng-class=\"{active:activeLink(link)}\" navbar-link></li>\n" +
    "    </ul>\n" +
    "    <ul ng-if=\"navbar.itemsRight\" class=\"nav navbar-nav navbar-right\">\n" +
    "        <li ng-repeat=\"link in navbar.itemsRight\" ng-class=\"{active:activeLink(link)}\" navbar-link></li>\n" +
    "    </ul>\n" +
    "    <div class=\"sidebar navbar-{{navbar.theme}}\" role=\"navigation\">\n" +
    "        <div class=\"sidebar-nav sidebar-collapse\" bs-collapse-target>\n" +
    "            <ul id=\"side-menu\" class=\"nav nav-side\">\n" +
    "                <li ng-if=\"navbar.search\" class=\"sidebar-search\">\n" +
    "                    <div class=\"input-group custom-search-form\">\n" +
    "                        <input class=\"form-control\" type=\"text\" placeholder=\"Search...\">\n" +
    "                        <span class=\"input-group-btn\">\n" +
    "                            <button class=\"btn btn-default\" type=\"button\" ng-click=\"search()\">\n" +
    "                                <i class=\"fa fa-search\"></i>\n" +
    "                            </button>\n" +
    "                        </span>\n" +
    "                    </div>\n" +
    "                </li>\n" +
    "                <li ng-repeat=\"link in navbar.items2\">\n" +
    "                    <a ng-if=\"!link.links\" href=\"{{link.href}}\">{{link.label || link.value || link.href}}</a>\n" +
    "                    <a ng-if=\"link.links\" href=\"{{link.href}}\" class=\"with-children\">{{link.label || link.value}}</a>\n" +
    "                    <a ng-if=\"link.links\" href=\"#\" class=\"pull-right toggle\" ng-click=\"togglePage($event)\">\n" +
    "                        <i class=\"fa\" ng-class=\"{'fa-chevron-left': !link.active, 'fa-chevron-down': link.active}\"></i></a>\n" +
    "                    <ul ng-if=\"link.links\" class=\"nav nav-second-level collapse\" ng-class=\"{in: link.active}\">\n" +
    "                        <li ng-repeat=\"link in link.links\">\n" +
    "                            <a ng-if=\"!link.vars\" href=\"{{link.href}}\" ng-click=\"loadPage($event)\">{{link.label || link.value}}</a>\n" +
    "                        </li>\n" +
    "                    </ul>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</nav>");
}]);

angular.module("nav/templates/sidebar.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("nav/templates/sidebar.tpl.html",
    "<navbar class=\"sidebar-navbar\"></navbar>\n" +
    "<aside ng-repeat=\"sidebar in sidebars\" class=\"sidebar sidebar-{{ sidebar.position }}\"\n" +
    "ng-class=\"{'sidebar-fixed':sidebar.fixed}\" bs-collapse>\n" +
    "    <div class=\"nav-panel\">\n" +
    "        <div ng-if=\"sidebar.user\">\n" +
    "            <div ng-if=\"sidebar.user.avatar_url\" class=\"pull-{{ sidebar.position }} image\">\n" +
    "                <img ng-src=\"{{sidebar.user.avatar_url}}\" alt=\"User Image\" />\n" +
    "            </div>\n" +
    "            <div class=\"pull-left info\">\n" +
    "                <p>{{ sidebar.infoText }}</p>\n" +
    "                <a href=\"#\">{{sidebar.user.name}}</a>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "    <ul class=\"sidebar-menu\">\n" +
    "        <li ng-if=\"section.name\" ng-repeat-start=\"section in sidebar.sections\" class=\"header\">\n" +
    "            {{section.name}}\n" +
    "        </li>\n" +
    "        <li ng-repeat-end ng-repeat=\"link in section.items\" class=\"treeview\"\n" +
    "        ng-class=\"{active:activeLink(link)}\" ng-include=\"'subnav'\"></li>\n" +
    "    </ul>\n" +
    "</aside>\n" +
    "<div class=\"sidebar-page\" ng-click=\"closeSideBar()\" full-page>\n" +
    "    <div class=\"content-wrapper\"></div>\n" +
    "    <div class=\"overlay\"></div>\n" +
    "</div>\n" +
    "\n" +
    "<script type=\"text/ng-template\" id=\"subnav\">\n" +
    "    <a ng-href=\"{{link.href}}\" ng-attr-title=\"{{link.title}}\" ng-click=\"menuCollapse($event)\">\n" +
    "        <i ng-if=\"link.icon\" class=\"{{link.icon}}\"></i>\n" +
    "        <span>{{link.name}}</span>\n" +
    "        <i ng-if=\"link.subitems\" class=\"fa fa-angle-left pull-right\"></i>\n" +
    "    </a>\n" +
    "    <ul class=\"treeview-menu\" ng-class=\"link.class\" ng-if=\"link.subitems\">\n" +
    "        <li ng-repeat=\"link in link.subitems\" ng-class=\"{active:activeLink(link)}\" ng-include=\"'subnav'\">\n" +
    "        </li>\n" +
    "    </ul>\n" +
    "</script>");
}]);
