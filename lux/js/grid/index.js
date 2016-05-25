import _ from '../ng';

// lux.nav module
var luxGridModule = _.module('lux.grid', ['lux']);

// Data providers
import luxGrid from './provider';
luxGridModule.config(luxGrid);


import luxGridDirective from './directive';
luxGridModule.directive('luxGrid', luxGridDirective);


import registerProviders from './register';
luxGridModule.config(registerProviders);

import menuConfig from './menu';
luxGridModule.config(menuConfig);
