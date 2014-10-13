
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
        search: false,
        url: lux.context.url
    };

    angular.module('lux.nav', ['templates-nav', 'lux.services', 'mgcrea.ngStrap.collapse'])
        .service('navService', function () {

            this.initScope = function (opts) {
                var navbar = extend({}, navBarDefaults, getOptions(opts));
                // Fix defaults
                if (!navbar.url)
                    navbar.url = lux.context.url || '/';
                if (!navbar.themeTop)
                    navbar.themeTop = navbar.theme;
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
        })
        .controller('Navigation', ['$scope', '$lux', function ($scope, $lux) {
            $lux.log.info('Setting up navigation on page');
            //
            var navbar = $scope.navbar = angular.extend({}, navBarDefaults, $scope.navbar),
                maybeCollapse = function () {
                    var width = window.innerWidth > 0 ? window.innerWidth : screen.width,
                        c = navbar.collapse;
                    if (width < navbar.collapseWidth)
                        navbar.collapse = 'collapse';
                    else
                        navbar.collapse = '';
                    return c !== navbar.collapse;
                };
            // Fix defaults
            if (!navbar.url)
                navbar.url = lux.context.url || '/';
            if (!navbar.themeTop)
                navbar.themeTop = navbar.theme;

            maybeCollapse();
            //
            windowResize(function () {
                if (maybeCollapse())
                    $scope.$apply();
            });
            //
            // Search
            $scope.search = function () {
                if (scope.search_text) {
                    window.location.href = '/search?' + $.param({q: $scope.search_text});
                }
            };

        }])
    //
    //  Directive for the navbar
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
            }
        };
    }])
    //
    //  Directive for the navbar with sidebar (nivebar2 template)
    .directive('navbar2', function () {
        return {
            templateUrl: "nav/navbar2.tpl.html",
            restrict: 'AE'
        };
    })
    //
    // Directive for the main page in the sidebar2 template
    .directive('navbar2Page', function () {
        return {
            compile: function () {
                return {
                    pre: function (scope, element, attrs) {
                        element.addClass('navbar2-page');
                        attrs.$set('style', 'min-height: ' + windowHeight() + 'px');
                    }
                };
            }
        };
    });