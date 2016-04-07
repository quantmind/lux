define(['angular',
        'lux/main',
        'angular-animate',
        'angular-ui-bootstrap',
        'lux/nav/templates'], function (angular, lux) {
    'use strict';
    //
    //  Lux Navigation module
    //  ============================
    //
    //  Html:
    //
    //      <navbar data-options="lux.context.navbar"></navbar>
    //
    //  Js:
    //
    //      lux.context.navbar = {
    //          id: null,           //  id attribute of the nav tag
    //          brand: null,        //  brand text to be displayed
    //          brandImage: null    //  brand image to be displayed rather than text. If available
    //                              //  the `brand` text is placed in the `alt` attribute
    //          url: "/",           //  href of the brand (if brand is defined)
    //      };
    //
    angular.module('lux.nav', ['ui.bootstrap', 'lux.nav.templates', 'ngAnimate'])
        //
        .value('navBarDefaults', {
            collapseWidth: 768,
            theme: 'default',
            search_text: '',
            isCollapsed: false,
            // Navigation place on top of the page (add navbar-static-top class to navbar)
            // nabar2 it is always placed on top
            top: false,
            // Fixed navbar
            fixed: false,
            search: false,
            url: '/',
            target: '_self',
            toggle: true,
            fluid: true,
            template: 'lux/nav/templates/navbar.tpl.html'
        })
        //
        .value('navLinkTemplate', 'lux/nav/templates/link.tpl.html')

        .factory('navLinks', ['$location', function ($location) {

            return {
                click: click,
                activeLink: activeLink,
                activeSubmenu: activeSubmenu
            };

            function click (e, link) {
                if (link.action) {
                    var func = link.action;
                    if (func)
                        func(e, link.href, link);
                }
            }

            // Check if a url is active
            function activeLink (url) {
                var loc;
                if (url)
                // Check if any submenus/sublinks are active
                    if (url.subitems && url.subitems.length > 0) {
                        if (exploreSubmenus(url.subitems)) return true;
                    }
                url = angular.isString(url) ? url : url.href || url.url;
                if (!url) return;
                if (lux.isAbsolute.test(url))
                    loc = $location.absUrl();
                else
                    loc = $location.path();
                var rest = loc.substring(url.length),
                    base = url.length < loc.length ? false : loc.substring(0, url.length),
                    folder = url.substring(url.length - 1) === '/';
                return base === url && (folder || (rest === '' || rest.substring(0, 1) === '/'));
            }

            function activeSubmenu (url) {
                var active = false;

                if (url.href && url.href === '#' && url.subitems.length > 0) {
                    active = exploreSubmenus(url.subitems);
                } else {
                    active = false;
                }
                return active;
            }

            // recursively loops through arrays to
            // find url match
            function exploreSubmenus(array) {
                for (var i = 0; i < array.length; i++) {
                    if (array[i].href === $location.path()) {
                        return true;
                    } else if (array[i].subitems && array[i].subitems.length > 0) {
                        if (exploreSubmenus(array[i].subitems)) return true;
                    }
                }
            }
        }])

        .factory('luxNavbar', ['navBarDefaults', '$window', function (navBarDefaults, $window) {

            function luxNavbar (opts) {
                var navbar = angular.extend({}, navBarDefaults, opts);

                if (!navbar.url)
                    navbar.url = '/';
                if (!navbar.themeTop)
                    navbar.themeTop = navbar.theme;
                navbar.container = navbar.fluid ? 'container-fluid' : 'container';

                luxNavbar.maybeCollapse(navbar);

                return navbar;
            }

            luxNavbar.template = function () {
                return navBarDefaults.template;
            };

            luxNavbar.maybeCollapse = function (navbar) {
                var width = $window.innerWidth > 0 ? $window.innerWidth : screen.width,
                    c = navbar.isCollapsed;

                navbar.isCollapsed = width < navbar.collapseWidth;
                return c !== navbar.isCollapsed;
            };

            luxNavbar.collapseForWide = function (navbar, element) {
                var width = $window.innerWidth > 0 ? $window.innerWidth : screen.width,
                    c = navbar.isCollapsed;

                if (width > navbar.collapseWidth || !navbar.isCollapsed) {
                    // If dropdown was opened then collapse
                    if (element.find('nav')[1].classList.contains('in'))
                        navbar.isCollapsed = true;
                }
                return c !== navbar.isCollapsed;
            };

            return luxNavbar;
        }])
        //
        .directive('fullPage', ['$window', function ($window) {

            return {
                restrict: 'AE',

                link: function (scope, element, attrs) {
                    var opts = angular.extend({}, scope.fullPage, lux.getOptions(attrs, 'fullPage')),
                        offset = +(opts.offset || 0),
                        height = $window.innerHeight - offset;
                    element.css('min-height', height + 'px');

                    scope.$watch(function () {
                        return $window.innerHeight - offset;
                    }, function (value) {
                        element.css('min-height', value + 'px');
                    });
                }
            };
        }])
        //
        .directive('navbarLink', ['navLinkTemplate', function (navLinkTemplate) {
            return {
                templateUrl: navLinkTemplate,
                restrict: 'A'
            };
        }])
        //
        //  Directive for the simple navbar
        //  This directive does not require the Navigation controller
        //      - items         -> Top left navigation
        //      - itemsRight    -> Top right navigation
        .directive('navbar', ['luxNavbar', 'navLinks', function (luxNavbar, navLinks) {
            //
            return {
                templateUrl: luxNavbar.template(),
                restrict: 'AE',
                link: navbar
            };
            //
            function navbar (scope, element, attrs) {

                var opts = angular.extend({}, scope.navbar, lux.getOptions(attrs, 'navbar'));

                scope.navbar = luxNavbar(opts);
                scope.links = navLinks;
                //
                lux.windowResize(function () {
                    if (luxNavbar.collapseForWide(scope.navbar, element))
                        scope.$apply();
                });
                //
                // When using ui-router, and a view changes collapse the
                //  navigation if needed
                scope.$on('$locationChangeSuccess', function () {
                    luxNavbar.maybeCollapse(scope.navbar);
                    //scope.$apply();
                });
            }
        }]);

});
