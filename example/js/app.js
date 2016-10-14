require([
    'require.config',
    'angular',
    '../../build/lux'
], function(lux, angular) {
    'use strict';

    angular.bootstrap('website', ['lux.form', 'lux.cms', 'lux.nav']);
});
