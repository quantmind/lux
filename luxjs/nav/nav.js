
    //
    //  Lux Navigation module
    //
    //  * Requires "angular-strap" for the collapsable directives
    //
    //  Include this module to render bootstrap navigation templates
    //  The navigation should be available as the ``navbar`` object within
    //  the ``luxContext`` object:
    //
    //      luxContext.navbar = {
    //          items: [{href="/", value="Home"}]
    //      };
    //
    var navBarDefaults = {
        collapseWidth: 768,
        theme: 'default',
        search_text: '',
        collapse: '',
        top: false,
        search: false,
        url: lux.context.url,
        target: '',
        fluid: true
    };

    angular.module('lux.nav', ['templates-nav', 'lux.services', 'mgcrea.ngStrap.collapse'])
        //
        .service('navService', ['$location', function ($location) {

            this.initScope = function (opts) {
                var navbar = extend({}, navBarDefaults, getOptions(opts));
                if (!navbar.url)
                    navbar.url = '/';
                if (!navbar.themeTop)
                    navbar.themeTop = navbar.theme;
                navbar.container = navbar.fluid ? 'container-fluid' : 'container';
                this.maybeCollapse(navbar);
                return navbar;
            };

            this.maybeCollapse = function (navbar) {
                var width = window.innerWidth > 0 ? window.innerWidth : screen.width,
                    c = navbar.collapse;
                if (width < navbar.collapseWidth)
                    navbar.collapse = 'collapse';
                else
                    navbar.collapse = '';
                return c !== navbar.collapse;
            };

            // Check if a url is active
            this.activeLink = function (url) {
                var loc;
                if (url)
                    url = typeof(url) === 'string' ? url : url.href || url.url;
                if (isAbsolute.test(url))
                    loc = $location.absUrl();
                else
                    loc = $location.path();
                var rest = loc.substring(url.length),
                    base = loc.substring(0, url.length),
                    folder = url.substring(url.length-1) === '/';
                return base === url && (folder || (rest === '' || rest.substring(0, 1) === '/'));
            };
        }])
        //
        //  Directive for the simple navbar
        //  This directive does not require the Navigation controller
        .directive('navbar', ['navService', function (navService) {
            //
            return {
                templateUrl: "nav/navbar.tpl.html",
                restrict: 'AE',
                // Create an isolated scope
                scope: {},
                // Link function
                link: function (scope, element, attrs) {
                    scope.navbar = navService.initScope(attrs);
                    scope.activeLink = navService.activeLink;
                    //
                    windowResize(function () {
                        if (navService.maybeCollapse(scope.navbar))
                            scope.$apply();
                    });
                }
            };
        }])
        //
        //  Directive for the navbar with sidebar (nivebar2 template)
        .directive('navbar2', ['navService', '$compile', function (navService, $compile) {
            return {
                restrict: 'AE',
                // Link function
                link: function (scope, element, attrs) {
                    scope.navbar2Content = element.children();
                    scope.navbar = navService.initScope(attrs);
                    scope.activeLink = navService.activeLink;
                    var inner = $compile('<nav-side-bar></nav-side-bar>')(scope);
                    element.append(inner);
                    //
                    windowResize(function () {
                        if (navService.maybeCollapse(scope.navbar))
                            scope.$apply();
                    });
                }
            };
        }])
        //
        //  Directive for the navbar with sidebar (nivebar2 template)
        .directive('navSideBar', function () {
            return {
                templateUrl: "nav/navbar2.tpl.html",
                restrict: 'E'
            };
        })
        //
        // Directive for the main page in the sidebar2 template
        .directive('navbar2Page', function () {
            return {
                compile: function () {
                    return {
                        pre: function (scope, element, attrs) {
                            element.append(scope.navbar2Content);
                            attrs.$set('style', 'min-height: ' + windowHeight() + 'px');
                        }
                    };
                }
            };
        });