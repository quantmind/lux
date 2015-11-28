(function () {
    'use strict';
    var config;

    var localRequiredPath = lux.PATH_TO_LOCAL_REQUIRED_FILES || '';

    var requiredFiles = {
        'lux': 'lux/lux'
    };

    config = {
        paths: requiredFiles,
        shim: {}
    };

    if (lux.PATH_TO_LOCAL_REQUIRED_FILES) {
        config.paths.lux = 'deps/lux';
        config.baseUrl = 'js';
    }

    lux.config(config);
}());
