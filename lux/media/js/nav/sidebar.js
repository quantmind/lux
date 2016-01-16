define(['angular',
        'lux',
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
            collapse: true,
            toggle: 'Menu',
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

                function close () {
                    element.removeClass('sidebar-open-left sidebar-open-right');
                }

                function toggle (e, position) {
                    e.preventDefault();
                    element.toggleClass('sidebar-open-' + position);
                }

                function add(sidebar, position) {
                    sidebar = angular.extend({
                        position: position,
                        menuCollapse: menuCollapse,
                        close: close,
                        toggle: toggle}, sidebarDefaults, sidebar);

                    if (sidebar.sections) {
                        if (!sidebar.collapse)
                            element.addClass('sidebar-open-' + sidebar.position);
                        sidebars.push(sidebar);
                        return sidebar;
                    }
                }
            }

            luxSidebars.template = function () {
                return sidebarDefaults.template;
            };

            // Initialise top navigation bar
            luxSidebars.navBar = function (navbar, sidebars) {
                navbar || (navbar = {});
                navbar.fixed = false;
                navbar.top = true;
                //
                // Add toggle to the navbar
                lux.forEach(sidebars, function (sidebar) {
                    if (sidebar.toggle) {
                        if (!navbar.itemsLeft) navbar.itemsLeft = [];

                        navbar.itemsLeft.splice(0, 0, {
                            href: sidebar.position,
                            title: sidebar.toggle,
                            name: sidebar.toggle,
                            klass: 'sidebar-toggle',
                            icon: 'fa fa-bars',
                            action: 'toggleSidebar',
                            right: 'vert-divider'
                        });
                    }
                });

                return navbar;
            }

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
                return {
                    restrict: 'AE',
                    compile: compile
                };

                function compile (element) {
                    var inner = element.html();
                    //
                    element.html('');

                    return {
                        pre: sidebar,
                        post: finalise
                    };

                    function sidebar(scope, element, attrs) {
                        var options = lux.getOptions(attrs),
                            sidebars = angular.extend({}, scope.sidebar, options),
                            navbar = angular.extend({}, scope.navbar, options.navbar),
                            template;

                        sidebars = luxSidebars(element, sidebars);

                        if (sidebars.length) {
                            scope.sidebars = sidebars;
                            template = $templateCache.get(luxSidebars.template());
                        } else
                            template = $templateCache.get(luxNavbar.template());

                        scope.navbar = luxSidebars.navBar(navbar, sidebars);
                        scope.links = navLinks;

                        element.append($compile(template)(scope));
                        inner = $compile(inner)(scope);

                        if (sidebars.length)
                            lux.querySelector(element, '.content-wrapper').append(inner);
                        else
                            element.after(inner);
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
                }
            }]);

});
