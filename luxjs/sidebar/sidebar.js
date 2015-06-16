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
        fixed: true,
        url: lux.context.url,
    };

    angular.module('bmll.sidebar', ['templates-sidebar', 'lux.nav'])
        //
        .service('sidebarService', ['linkService', function (linkService) {

            this.initScope = function (scope, opts, element) {

                var sidebar = angular.extend({}, sidebarDefaults, lux.getOptions(opts)),
                    body = lux.querySelector(document, 'body');

                if (!sidebar.url)
                    sidebar.url = '/';
                if (!sidebar.themeTop)
                    sidebar.themeTop = sidebar.theme;
                if (!sidebar.position)
                    sidebar.position = sidebarDefaults.position;

                sidebar.container = sidebar.fluid ? 'container-fluid' : 'container';
                body.addClass(sidebar.position + '-sidebar skin');

                // Add link service functionality
                linkService.initScope(scope);

                if (scope.user) {
                    if (!sidebar.collapse)
                        element.addClass('sidebar-open-' + sidebar.position);
                }

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
                return sidebar;
            };
        }])
        //
        .directive('navSidebarLink', ['sidebarService', function (sidebarService) {
            return {
                templateUrl: "sidebar/nav-link.tpl.html",
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
                templateUrl: "sidebar/sidebar.tpl.html",

                restrict: 'A',

                link: function (scope, element, attrs) {
                    var sidebar = scope.sidebar,
                        // get the original content
                        content = scope.sidebarContent,
                        // content-wrapper
                        wrapper = angular.element(document.createElement('div'))
                                    .addClass('content-wrapper')
                                    .append(content),
                        // overlay
                        overlay = angular.element(document.createElement('div'))
                                    .addClass('overlay'),
                        // page
                        page = angular.element(document.createElement('div'))
                                    .attr('id', 'page')
                                    .append(wrapper)
                                    .append(overlay);

                    delete scope.sidebarContent;

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
