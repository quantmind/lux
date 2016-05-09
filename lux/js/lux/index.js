import _ from '../ng';

const luxModule = _.module('lux', []);

// Provider
import luxLazy from './lazy';
luxModule.provider('luxLazy', luxLazy);

// Factory
import $lux from './api';
luxModule.factory('$lux', $lux);
