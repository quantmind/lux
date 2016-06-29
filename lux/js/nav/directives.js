import {getOptions} from '../core/utils';
import querySelector from '../core/queryselector';
import _ from '../ng';


// @ngInject
export function link ($lux, luxLinkTemplate, luxDropdownTemplate, luxLink) {
    return {
        restrict: 'A',
        link: linkLink
    };

    function linkLink ($scope, $element) {
        var link = $scope.link || {},
            template;

        $scope.links = luxLink;

        if (link.items) {
            link.id = link.id || $lux.id();
            template = luxDropdownTemplate;
            $element.replaceWith($lux.$compile(template)($scope));
        }
        else {
            template = luxLinkTemplate;
            $element.append($lux.$compile(template)($scope));
        }
    }
}

// @ngInject
export function navbar ($window, luxNavbarTemplate, luxNavbar) {
    //
    return {
        template: luxNavbarTemplate,
        restrict: 'E',
        link: navbar
    };
    //
    function navbar (scope, element, attrs) {
        scope.navbar = luxNavbar(_.extend({}, scope.navbar, getOptions($window, attrs, 'navbar')));
        scope.navbar.element = element[0];
    }
}

// @ngInject
export function tabs ($lux, luxTabsTemplate, luxLink) {
    //
    return {
        template: luxTabsTemplate,
        restrict: 'AE',
        scope: {
            tabs: '='
        },
        controller: TabsCtrl
    };
    //
    // @ngInject
    function TabsCtrl ($scope) {
        $scope.links = luxLink;
    }
}

// @ngInject
export function sidebar ($window, $compile, $timeout, luxSidebarTemplate, luxSidebar) {
    //
    let inner;

    return {
        restrict: 'E',
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
        let template;

        var sidebar = _.extend({}, scope.sidebar, getOptions($window, attrs, 'sidebar')),
            navbar = _.extend({}, scope.navbar, sidebar.navbar);

        navbar.top = true;
        navbar.fixed = true;
        navbar.fluid = true;
        scope.navbar = navbar;
        delete scope.sidebar;

        const sidebars = luxSidebar(sidebar);

        if (sidebars.length) {
            scope.sidebars = sidebars;
            scope.closeSidebars = closeSidebars;
            //
            // Add toggle to the navbar
            _.forEach(sidebars, function (sidebar) {
                addSidebarToggle(sidebar, scope);
            });
            //
            template = luxSidebarTemplate;
        } else
            template = `<lux-navbar></lux-navbar>`;

        element.append($compile(template)(scope));

        if (inner) {
            inner = $compile(inner)(scope);

            if (sidebars.length)
                querySelector(element, '.sidebar-page').append(inner);
            else
                element.after(inner);
        }

        function closeSidebars () {
            _.forEach(sidebars, function (sidebar) {
                sidebar.close();
            });
        }
    }

    function finalise(scope, element) {
        var triggered = false;

        $timeout(function () {
            return element.find('nav');
        }).then(function (nav) {

            _.element($window).bind('scroll', function () {

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


//
//  Add toggle functionality to sidebar
function addSidebarToggle (sidebar, scope) {
    if (!sidebar.toggleName) return;

    sidebar.close = function () {
        setState(false);
    };

    function toggle (e) {
        e.preventDefault();
        _.forEach(scope.sidebars, function (s) {
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
