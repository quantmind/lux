import _ from '../ng';


// lux.form module
var luxFormModule = _.module('lux.form', ['lux']);

// Provider
import luxFormConfig from './provider';
luxFormModule.provider('luxFormConfig', luxFormConfig);


// Directives
import * as directives from './directives';
luxFormModule.directive('luxForm', directives.luxForm);
luxFormModule.directive('luxField', directives.luxField);


import formDefaults from './types-default';
formDefaults(luxFormModule);

import formWrappers from './wrappers';
formWrappers(luxFormModule);
