import _ from '../ng';

const luxModule = _.module('lux', []);

// Provider
import luxLazy from './lazy';
luxModule.provider('luxLazy', luxLazy);

// Factories
import luxMessage from './message';
import $lux from './api';
luxModule.factory('luxMessage', luxMessage);
luxModule.factory('$lux', $lux);

// Directives
import luxPage from './page';
luxModule.directive('luxPage', luxPage);
