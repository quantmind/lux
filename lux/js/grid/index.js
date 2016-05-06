import _ from '../ng';

// lux.nav module
var luxGridModule = _.module('lux.grid', ['lux']);

// Data providers
import luxGridConfig from './provider';
luxGridModule.provider('luxGridConfig', luxGridConfig);


import luxGridDirective from './directive';
luxGridModule.directive('luxGrid', luxGridDirective);


import luxGridRun from './run';
luxGridModule.run(luxGridRun);
