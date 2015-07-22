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
    var sidebarDefaults = {
        collapse: true,
        position: 'left',
        toggle: 'Menu',
        url: lux.context.url || '/',
    };

    angular.module('lux.sidebar', ['lux.nav'])
        //
        .service('sidebarService', ['linkService', 'navService', function (linkService, navService) {

            this.initScope = function (scope, opts, element) {

                var sidebar = angular.extend({}, sidebarDefaults, scope.sidebar, lux.getOptions(opts)),
                    body = lux.querySelector(document, 'body');

                sidebar.container = sidebar.fluid ? 'container-fluid' : 'container';
                body.addClass(sidebar.position + '-sidebar skin');

                // Add link service functionality
                linkService.initScope(scope);

                if (!sidebar.collapse)
                    element.addClass('sidebar-open-' + sidebar.position);

                scope.toggleSidebar = function() {
                    element.toggleClass('sidebar-open-' + sidebar.position);
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

                scope.sidebar = sidebar;
                scope.navbar = initNavbar(sidebar);

                if (!sidebar.sections && scope.navigation)
                    sidebar.sections = scope.navigation;
                return sidebar;
            };

            // Initialise top navigation bar
            function initNavbar (sidebar) {
                var navbar = sidebar.navbar;

                // No navbar, add an object
                if (!navbar)
                    sidebar.navbar = navbar = {};
                //
                // Add toggle to the navbar
                if (sidebar.toggle) {
                    if (!navbar.itemsLeft) navbar.itemsLeft = [];

                    navbar.itemsLeft.splice(0, 0, {
                        href: '#',
                        title: sidebar.toggle,
                        name: sidebar.toggle,
                        klass: 'sidebar-toggle',
                        icon: 'fa fa-bars',
                        action: 'toggleSidebar'
                    });
                }

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
        .directive('sidebar', ['$compile', 'sidebarService', function ($compile, sidebarService) {
            //
            return {
                restrict: 'AE',

                // We need to use the compile function so that we remove the
                // content before it is included in the bootstraping algorithm
                compile: function compile(element) {
                    var inner = element.html(),
                        className = element[0].className;
                    //
                    element.html('');

                    return {
                        post: function (scope, element, attrs) {
                            scope.sidebarContent = inner;
                            sidebarService.initScope(scope, attrs, element);

                            inner = $compile('<div data-content-sidebar bs-collapse></div>')(scope);
                            element.append(inner);
                        }
                    };
                }
            };
        }])

        //
        //  Inner directive for the sidebar
        .directive('contentSidebar', ['$compile', '$document', function ($compile, $document) {
            return {
                templateUrl: "nav/templates/sidebar.tpl.html",

                restrict: 'A',

                link: function (scope, element, attrs) {
                    var sidebar = scope.sidebar,
                        // get the original content
                        content = scope.sidebarContent,
                        // page
                        page = angular.element(document.createElement('div'));

                    delete scope.sidebarContent;

                    if (sidebar.sections) {
                        // content-wrapper
                        var wrapper = angular.element(document.createElement('div'))
                                        .addClass('content-wrapper')
                                        .append(content),
                            // overlay
                            overlay = angular.element(document.createElement('div'))
                                        .addClass('overlay');

                        page.append(wrapper).append(overlay).addClass('sidebar-page');
                    } else
                        page.append(content).addClass('navbar-page');

                    // compile
                    page = $compile(page)(scope);
                    element.after(page);

                    page.on('click', function() {
                        var sidebarTag = page.parent();
                        if (sidebarTag.hasClass('sidebar-open-left')) {
                            sidebarTag.removeClass('sidebar-open-left');
                        }

                        if (sidebarTag.hasClass('sidebar-open-right')) {
                            sidebarTag.removeClass('sidebar-open-right');
                        }
                    });
                }
            };
        }]);
