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
import luxRemote from './remote';
luxFormModule.directive('luxRemote', luxRemote);

// Default types, wrappers and actions

import formDefaults from './types';
formDefaults(luxFormModule);

import formWrappers from './wrappers';
formWrappers(luxFormModule);

import formActions from './actions';
formActions(luxFormModule);

import formMessages from './messages';
formMessages(luxFormModule);


// Run configuration
import runForm from './run';
luxFormModule.run(runForm);
