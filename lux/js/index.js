import _ from './ng';

import * as core from './core';

const luxModule = _.module('lux', []);

luxModule.factory('$lux', core.lux);


import './form';
import './nav';


export {version} from '../../package.json';
export {default as querySelector} from './core/queryselector';
export {default as s4} from './core/s4';
export {noop, urlBase64Decode, joinUrl, getOptions, isAbsolute} from './core/utils';
