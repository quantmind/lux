import _ from '../ng';

// lux.nav module
var luxNavModule = _.module('lux.nav', ['lux']);


// Constants
import * as constants from './constants';
luxNavModule.constant('luxLinkTemplate', constants.linkTemplate);
luxNavModule.constant('luxNavbarTemplate', constants.navbarTemplate);
luxNavModule.constant('luxSidebarTemplate', constants.sidebarTemplate);
luxNavModule.constant('luxNavBarDefaults', constants.navbarDefaults);
luxNavModule.constant('luxSidebarDefaults', constants.sidebarDefaults);
luxNavModule.constant('luxDropdownTemplate', constants.luxDropdownTemplate);


// Factories
import * as factories from './factories';
luxNavModule.factory('luxLink', factories.link);
luxNavModule.factory('luxNavbar', factories.navbar);
luxNavModule.factory('luxSidebar', factories.sidebar);


// Directives
import * as directives from './directives';
luxNavModule.directive('luxLink', directives.link);
luxNavModule.directive('luxNavbar', directives.navbar);
luxNavModule.directive('luxSidebar', directives.sidebar);
