// some versions of angular don't export the angular module properly,
// so we get it from window in this case.
//let angular = require('angular');
//if (!angular || !angular.version) angular = window.angular;
import {default as angular} from 'angular';
export default angular;
