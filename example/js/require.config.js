/* eslint-plugin-disable angular */
define(['lux/config/main'], function (lux) {
    'use strict';

    var localRequiredPath = lux.PATH_TO_LOCAL_REQUIRED_FILES || '';

    lux.require.paths = lux.extend(lux.require.paths, {
        'angular-img-crop': localRequiredPath + 'luxsite/ng-img-crop.js',
        'videojs': '//vjs.zencdn.net/4.12/video.js'
    });

    // lux.require.shim = lux.extend(lux.require.shim, {});

    lux.config();

    return lux;
});
