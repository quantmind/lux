define(['angular',
        'lux/main'], function (angular, lux) {
    'use strict';

    //
    angular.module('lux.scroll.change', [])
        //
        .constant('scrollChangeDefaults', {
            distance: 200
        })
        //
        .factory('currentYPosition', ['$window', '$document',
            function ($window, $document) {

                return function () {
                    // Firefox, Chrome, Opera, Safari
                    if ($window.pageYOffset) {
                        return $window.pageYOffset;
                    }
                    // Internet Explorer 6 - standards mode
                    if ($document[0].documentElement && $document[0].documentElement.scrollTop) {
                        return $document[0].documentElement.scrollTop;
                    }
                    // Internet Explorer 6, 7 and 8
                    if ($document[0].body.scrollTop) {
                        return $document[0].body.scrollTop;
                    }
                    return 0;
                };
            }]
        )
        //
        .directive('scrollChange', ['$window', 'currentYPosition', 'scrollChangeDefaults',
            function ($window, currentYPosition, scrollChangeDefaults) {
                return {
                    link: {
                        post: postLink
                    }
                };

                function postLink (scope, element, attrs) {
                    var opts = lux.getOptions(attrs, 'scrollChange');
                    opts = angular.extend({}, scrollChangeDefaults, opts);

                    angular.element($window).bind('scroll', function () {
                        fire();
                    });

                    fire();

                    function fire () {
                        var pos = currentYPosition(),
                            pct = Math.min(opts.distance, pos)/opts.distance;
                        if (opts.callback)
                            opts.callback(pct);
                    }
                }
            }]
        );

});
