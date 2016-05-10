import _ from '../ng';

const cmsModule = _.module('lux.cms', ['lux']);

// Directives
import * as directives from './directives';
cmsModule.factory('luxMessages', directives.luxMessages);
