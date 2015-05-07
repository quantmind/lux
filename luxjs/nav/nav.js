
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
        // Navigation place on top of the page (add navbar-static-top class to navbar)
        // nabar2 it is always placed on top
        top: false,
        // Fixed navbar
        fixed: false,
        search: false,
        url: lux.context.url,
        target: '',
        toggle: true,
        fluid: true
    };

    angular.module('lux.nav', ['templates-nav', 'lux.services', 'lux.bs'])
        //
        .service('linkService', ['$location', function ($location) {

            this.initScope = function (scope, opts) {

                scope.clickLink = function (e, link) {
                    if (link.action) {
                        var func = scope[link.action];
                        if (func)
                            func(e, link.href, link);
                    }
                };

                // Check if a url is active
                scope.activeLink = function (url) {
                    var loc;
                    if (url)
                        url = typeof(url) === 'string' ? url : url.href || url.url;
                    if (!url) return;
                    if (isAbsolute.test(url))
                        loc = $location.absUrl();
                    else
                        loc = $location.path();
                    var rest = loc.substring(url.length),
                        base = loc.substring(0, url.length),
                        folder = url.substring(url.length-1) === '/';
                    return base === url && (folder || (rest === '' || rest.substring(0, 1) === '/'));
                };
            };
        }])

        .service('navService', ['linkService', function (linkService) {

            this.initScope = function (scope, opts) {

                var navbar = extend({}, navBarDefaults, getOptions(opts));
                if (!navbar.url)
                    navbar.url = '/';
                if (!navbar.themeTop)
                    navbar.themeTop = navbar.theme;
                navbar.container = navbar.fluid ? 'container-fluid' : 'container';

                this.maybeCollapse(navbar);

                linkService.initScope(scope);

                scope.navbar = navbar;

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
        }])
        //
        .directive('navbarLink', function () {
            return {
                templateUrl: "nav/link.tpl.html",
                restrict: 'A'
            };
        })
        //
        //  Directive for the simple navbar
        //  This directive does not require the Navigation controller
        .directive('navbar', ['navService', function (navService) {
            //
            return {
                templateUrl: "nav/navbar.tpl.html",
                restrict: 'AE',
                // Link function
                link: function (scope, element, attrs) {
                    navService.initScope(scope, attrs);
                    //
                    windowResize(function () {
                        if (navService.maybeCollapse(scope.navbar))
                            scope.$apply();
                    });
                    //
                    // When using ui-router, and a view changes collapse the
                    //  navigation if needed
                    scope.$on('$locationChangeSuccess', function () {
                        navService.maybeCollapse(scope.navbar);
                        //scope.$apply();
                    });
                }
            };
        }])
        //
        //  Directive for the navbar with sidebar (nivebar2 template)
        //      - items         -> Top left navigation
        //      - itemsRight    -> Top right navigation
        //      - items2        -> side navigation
        .directive('navbar2', ['navService', '$compile', function (navService, $compile) {
            return {
                restrict: 'AE',
                //
                scope: {},
                // We need to use the compile function so that we remove the
                // before it is included in the bootstraping algorithm
                compile: function compile(element) {
                    var inner = element.html(),
                        className = element[0].className;
                    //
                    element.html('');

                    return {
                        post: function (scope, element, attrs) {
                            scope.navbar2Content = inner;
                            navService.initScope(scope, attrs);

                            inner = $compile('<div data-nav-side-bar></div>')(scope);
                            element.replaceWith(inner.addClass(className));
                            //
                            windowResize(function () {
                                if (navService.maybeCollapse(scope.navbar))
                                    scope.$apply();
                            });
                        }
                    };
                }
            };
        }])
        //
        //  Directive for the navbar with sidebar (nivebar2 template)
        .directive('navSideBar', ['$compile', '$document', function ($compile, $document) {
            return {
                templateUrl: "nav/navbar2.tpl.html",

                restrict: 'A',

                link: function (scope, element, attrs) {
                    var navbar = scope.navbar;
                    element.addClass('navbar2-wrapper');
                    if (navbar && navbar.theme)
                        element.addClass('navbar-' + navbar.theme);
                    var inner = $($document[0].createElement('div')).addClass('navbar2-page')
                                    .append(scope.navbar2Content);
                    // compile
                    $compile(inner)(scope);
                    // and append
                    element.append(inner);
                    //
                    function resize() {
                        inner.attr('style', 'min-height: ' + windowHeight() + 'px');
                    }
                    //
                    windowResize(resize);
                    //
                    resize();
                }
            };
        }]);
