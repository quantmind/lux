import _ from '../ng';

// lux.nav module
var luxGridModule = _.module('lux.grid', ['lux']);

// Data providers
import luxGrid from './provider';
luxGridModule.provider('luxGrid', luxGrid);


import luxGridDirective from './directive';
luxGridModule.directive('luxGrid', luxGridDirective);


import registerProviders from './register';
luxGridModule.config(registerProviders);
