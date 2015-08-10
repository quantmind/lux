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
            infoText: 'Signed in as'
        })
        //
        .value('sidebarTemplate', "nav/templates/sidebar.tpl.html")
        //
        .value('navbarTemplate', "nav/templates/navbar.tpl.html")
        //
        .service('sidebarService', ['linkService', 'navService', 'sidebarDefaults',
                function (linkService, navService, sidebarDefaults) {

            function initSideBar (sidebars, element, sidebar, position) {
                sidebar = angular.extend({}, sidebarDefaults, sidebar);
                sidebar.position = position;
                if (!sidebar.collapse)
                    element.addClass('sidebar-open-' + position);
                if (sidebar.sections) {
                    sidebars.push(sidebar);
                    return sidebar;
                }
            }

            // Initialise scope and build left and right sidebar if available
            this.initScope = function (scope, opts, element) {

                var sidebar = angular.extend({}, scope.sidebar, lux.getOptions(opts)),
                    sidebars = [],
                    left = sidebar.left,
                    right = sidebar.right;

                if (left) initSideBar(sidebars, element, left, 'left');
                if (right) initSideBar(sidebars, element, right, 'right');
                if (!sidebars.length) initSideBar(sidebars, element, sidebar, 'left');

                scope.container = sidebar.fluid ? 'container-fluid' : 'container';

                // Add link service functionality
                linkService.initScope(scope);

                // Close sidebars
                scope.closeSideBar = function () {
                    element.removeClass('sidebar-open-left sidebar-open-right');
                };

                // Toggle the sidebar
                scope.toggleSidebar = function(e, position) {
                    e.preventDefault();
                    element.toggleClass('sidebar-open-' + position);
                };

                scope.menuCollapse = function($event) {
                    // Get the clicked link, the submenu and sidebar menu
                    var item = angular.element($event.currentTarget || $event.srcElement),
                        submenu = item.next();

                    // If the menu is not visible then close all open menus
                    if (submenu.hasClass('active')) {
                        item.removeClass('active');
                        submenu.removeClass('active');
                    } else {
                        item.parent().parent().find('ul').removeClass('active');
                        item.addClass('active');
                        submenu.addClass('active');
                    }
                };

                scope.navbar = initNavbar(sidebar.navbar, sidebars);
                navService.initScope(scope);
                return sidebars;
            };

            // Initialise top navigation bar
            function initNavbar (navbar, sidebars) {
                // No navbar, add an object
                if (!navbar)
                    navbar = {};
                navbar.fixed = true;
                navbar.top = true;
                //
                // Add toggle to the navbar
                forEach(sidebars, function (sidebar) {
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
        }])
        //
        .directive('navSidebarLink', ['sidebarService', function (sidebarService) {
            return {
                templateUrl: "nav/templates/nav-link.tpl.html",
                restrict: 'A',
            };
        }])
        //
        //  Directive for the sidebar
        .directive('sidebar', ['$compile', 'sidebarService', 'sidebarTemplate',
                               'navbarTemplate', '$templateCache',
                        function ($compile, sidebarService, sidebarTemplate, navbarTemplate,
                                  $templateCache, $sce) {
            //
            return {
                restrict: 'AE',

                // We need to use the compile function so that we remove the
                // content before it is included in the bootstraping algorithm
                compile: function compile(element) {
                    var inner = element.html();
                    //
                    element.html('');

                    return {
                        pre: function (scope, element, attrs) {
                            var sidebars = sidebarService.initScope(scope, attrs, element),
                                template;

                            if (sidebars.length) {
                                scope.sidebars = sidebars;
                                template = $templateCache.get(sidebarTemplate);
                            } else
                                template = $templateCache.get(navbarTemplate);

                            //element.replaceWith($compile(template)(scope));
                            element.append($compile(template)(scope));
                            inner = $compile(inner)(scope);

                            if (sidebars.length)
                                lux.querySelector(element, '.content-wrapper').append(inner);
                            else
                                element.after(inner);
                        }
                    };
                }
            };
        }]);
