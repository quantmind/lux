import _ from '../ng';

const luxModule = _.module('lux', []);

// Provider
import $lux from './provider';
luxModule.provider('$lux', $lux);

// Factories
import luxMessage from './message';
luxModule.factory('luxMessage', luxMessage);

// Directives
import luxPage from './page';
luxModule.directive('luxPage', luxPage);
