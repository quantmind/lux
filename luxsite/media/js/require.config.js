define(['lux/config'], function (lux) {
    'use strict';

    var localRequiredPath = lux.PATH_TO_LOCAL_REQUIRED_FILES || '';

    var requiredFiles = {
        'giotto': localRequiredPath + 'luxsite/giotto',
        'angular-img-crop': localRequiredPath + 'bmll/ng-img-crop.js',
        'angular-infinite-scroll': '//cdnjs.cloudflare.com/ajax/libs/ngInfiniteScroll/1.2.1/ng-infinite-scroll',
        'videojs': '//vjs.zencdn.net/4.12/video.js',
        'moment-timezone': '//cdnjs.cloudflare.com/ajax/libs/moment-timezone/0.4.0/moment-timezone-with-data-2010-2020'
    };

    lux.config({
        paths: requiredFiles,
        shim: {
            'angular-moment': {
                deps: ['angular', 'moment-timezone']
            }
        },
        waitSeconds: 60
    });

    return lux;
});
