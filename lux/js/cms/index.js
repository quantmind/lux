import _ from '../ng';

const cmsModule = _.module('lux.cms', ['lux']);

// Directives
import luxMessages from './messages';
import luxAce from './ace';

cmsModule.directive('luxMessages', luxMessages);
cmsModule.directive('luxAce', luxAce);
