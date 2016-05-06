import {isAbsolute} from '../core/utils';
import _ from '../ng';


// @ngInject
export function link($location) {

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
        url = _.isString(url) ? url : url.href || url.url;
        if (!url) return;
        if (isAbsolute.test(url))
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
}


// @ngInject
export function navbar(luxNavBarDefaults) {

    return luxNavbar;

    function luxNavbar (opts) {
        var navbar = _.extend({}, luxNavBarDefaults, opts);

        if (!navbar.url)
            navbar.url = '/';

        navbar.container = navbar.fluid ? 'container-fluid' : 'container';

        return navbar;
    }
}


// @ngInject
export function sidebar(luxSidebarDefaults) {

    return sidebar;

    function sidebar (opts) {
        opts || (opts = {});

        var sidebars = [];

        if (opts.left) add(opts.left, 'left');
        if (opts.right) add(opts.right, 'right');
        if (!sidebars.length) add(opts, 'left');

        return sidebars;

        // Add a sidebar (left or right position)
        function add(sidebar, position) {
            sidebar = _.extend({
                position: position,
                menuCollapse: menuCollapse
            }, luxSidebarDefaults, sidebar);

            if (sidebar.sections) {
                sidebars.push(sidebar);
                return sidebar;
            }
        }
    }

    function menuCollapse ($event) {
        // Get the clicked link, the submenu and sidebar menu
        var item = _.element($event.currentTarget || $event.srcElement),
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
}
