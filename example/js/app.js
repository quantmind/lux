require([
    'require.config',
    'angular',
    'lux/forms/main',
    'lux/services/main'
], function(lux) {
    'use strict';

    lux.bootstrap('website', ['lux.form', 'lux.restapi', 'lux.webapi']);
});
