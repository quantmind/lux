import angular from './angular-fix';

import * as core from './core';
import * as form from './form';

const luxModule = angular.module('lux', []);

luxModule.factory('$lux', core.lux);


var luxFormModule = angular.module('lux.form', ['lux']);


luxFormModule.constant('LuxFormElements', form.elements);
luxFormModule.directive('LuxForm', form.directive);
luxFormModule.factory('luxFormFactory', form.factory);


export {version} from '../../package.json';
export {noop, urlBase64Decode, joinUrl, getOptions} from './core/utils';
