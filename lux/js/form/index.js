import {default as _} from '../ng';

import luxFormConfig from './provider';
import luxFormFactory from './factory';
import luxForm from './directive';
import luxFormElements from './elements';
import form from './types-default';


// lux.form module
var luxFormModule = _.module('lux.form', ['lux']);

luxFormModule.provider('luxFormConfig', luxFormConfig);
luxFormModule.constant('luxFormElements', luxFormElements);
luxFormModule.directive('luxForm', luxForm);
luxFormModule.factory('luxFormFactory', luxFormFactory);


form(luxFormModule);
//types.checkbox(luxFormModule);
