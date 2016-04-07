define(['angular',
        'lux/main',
        'lux/nav/navbar'], function (angular, lux) {
    'use strict';
    //
    //  Sidebar module
    //
    //  Include this module to render bootstrap sidebar templates
    //  The sidebar should be available as the ``sidebar`` object within
    //  the ``luxContext`` object:
    //
    //      luxContext.sidebar = {
    //          sections: [{
    //              name: 'Sec1',
    //              items: [{
    //                      name: 'i1',
    //                      icon: 'fa fa-dashboard',
    //                      subitems: []
    //               }]
    //          }]
    //      };
    //
    angular.module('lux.sidebar', ['lux.nav'])
        //
        .value('sidebarDefaults', {
            open: false,
            toggleName: 'Menu',
            url: lux.context.url || '/',
            infoText: 'Signed in as',
            template: 'lux/nav/templates/sidebar.tpl.html'
        })
        //
        .factory('luxSidebars', ['sidebarDefaults', function (sidebarDefaults) {

            function luxSidebars (element, opts) {
                opts || (opts = {});

                var sidebars = [];

                if (opts.left) add(opts.left, 'left');
                if (opts.right) add(opts.right, 'right');
                if (!sidebars.length) add(opts, 'left');

                return sidebars;

                // Add a sidebar (left or right position)
                function add(sidebar, position) {
                    sidebar = angular.extend({
                        position: position,
                        menuCollapse: menuCollapse}, sidebarDefaults, sidebar);

                    if (sidebar.sections) {
                        sidebars.push(sidebar);
                        return sidebar;
                    }
                }
            }

            luxSidebars.template = function () {
                return sidebarDefaults.template;
            };

            return luxSidebars;

            function menuCollapse ($event) {
                // Get the clicked link, the submenu and sidebar menu
                var item = angular.element($event.currentTarget || $event.srcElement),
                    submenu = item.next();

                // If the menu is not visible then close all open menus
                if (submenu.hasClass('active')) {
                    item.removeClass('active');
                    submenu.removeClass('active');
                } else {
                    var itemRoot = item.parent().parent();
                    itemRoot.find('ul').removeClass('active');
                    itemRoot.find('li').removeClass('active');

                    item.parent().addClass('active');
                    submenu.addClass('active');
                }
            }
        }])
        //
        //  Directive for the sidebar
        .directive('sidebar', ['$compile', 'luxSidebars', 'luxNavbar', 'navLinks',
            '$templateCache', '$window', '$timeout',
            function ($compile, luxSidebars, luxNavbar, navLinks,
                      $templateCache, $window, $timeout) {
                //
                var inner;

                return {
                    restrict: 'AE',
                    compile: function (element) {
                        inner = element.html();

                        element.html('');

                        return {
                            pre: sidebar,
                            post: finalise
                        };
                    }
                };

                function sidebar(scope, element, attrs) {
                    var options = lux.getOptions(attrs, 'sidebar'),
                        sidebar = angular.extend({}, scope.sidebar, options),
                        navbar = luxNavbar(angular.extend({}, sidebar.navbar, options.navbar)),
                        template;

                    navbar.top = true;
                    navbar.fluid = true;
                    scope.navbar = navbar;
                    var sidebars = luxSidebars(element, sidebar);

                    if (sidebars.length) {
                        scope.sidebars = sidebars;
                        scope.closeSidebars = closeSidebars;
                        //
                        // Add toggle to the navbar
                        lux.forEach(sidebars, function (sidebar) {
                            addSidebarToggle(sidebar, scope);
                        });
                        //
                        template = $templateCache.get(luxSidebars.template());
                    } else
                        template = $templateCache.get(luxNavbar.template());

                    scope.links = navLinks;

                    element.append($compile(template)(scope));

                    if (inner) {
                        inner = $compile(inner)(scope);

                        if (sidebars.length)
                            lux.querySelector(element, '.sidebar-page').append(inner);
                        else
                            element.after(inner);
                    }

                    function closeSidebars () {
                        angular.forEach(sidebars, function (sidebar) {
                            sidebar.close();
                        });
                    }
                }

                function finalise(scope, element) {
                    var triggered = false;

                    $timeout(function () {
                        return element.find('nav');
                    }).then(function (nav) {

                        angular.element($window).bind('scroll', function () {

                            if ($window.pageYOffset > 150 && triggered === false) {
                                nav.addClass('navbar--small');
                                triggered = true;
                                scope.$apply();
                            } else if ($window.pageYOffset <= 150 && triggered === true) {
                                nav.removeClass('navbar--small');
                                triggered = false;
                                scope.$apply();
                            }

                        });
                    });
                }
            }]);

        //
        //  Add toggle functionality to sidebar
        function addSidebarToggle (sidebar, scope) {
            if (!sidebar.toggleName) return;

            sidebar.close = function () {
                setState(false);
            };

            function toggle (e) {
                e.preventDefault();
                angular.forEach(scope.sidebars, function (s) {
                    if (s != sidebar) s.close();
                });
                setState(!sidebar.open);
            }

            function setState (value) {
                sidebar.open = value;
                sidebar.closed = !value;
                scope.navbar[sidebar.position] = sidebar.open;
            }

            var item = {
                href: sidebar.position,
                title: sidebar.toggleName,
                name: sidebar.toggleName,
                klass: 'sidebar-toggle',
                icon: 'fa fa-bars',
                action: toggle,
                right: 'vert-divider'
            };

            if (sidebar.position === 'left') {
                if (!scope.navbar.itemsLeft) scope.navbar.itemsLeft = [];
                scope.navbar.itemsLeft.splice(0, 0, item);
            } else {
                if (!scope.navbar.itemsRight) scope.navbar.itemsRight = [];
                scope.navbar.itemsRight.push(item);
            }
        }
});
