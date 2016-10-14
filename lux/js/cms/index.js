import _ from '../ng';

const cmsModule = _.module('lux.cms', ['lux']);

// Directives
import luxMessages from './messages';
import luxAce from './ace';
import luxCrumbs from './crumbs';
import luxYear from './year';
import luxFullpage from './fullpage';
import luxFeature from './feature';

cmsModule.directive('luxMessages', luxMessages);
cmsModule.directive('luxAce', luxAce);
cmsModule.directive('luxCrumbs', luxCrumbs);
cmsModule.directive('luxYear', luxYear);
cmsModule.directive('luxFullpage', luxFullpage);
cmsModule.directive('luxFeature', luxFeature);
