define(['angular',
        'lux/main'], function (angular, lux) {
    'use strict';

    var root = lux.root;
    //
    //  Code highlighting with highlight.js
    //
    //  This module is added to the blog module so that the highlight
    //  directive can be used. Alternatively, include the module in the
    //  module to be bootstrapped.
    //
    //  Note:
    //      MAKE SURE THE lux.extensions.code EXTENSIONS IS INCLUDED IN
    //      YOUR CONFIG FILE
    angular.module('lux.highlight', [])

        .directive('luxHighlight', ['$rootScope', '$log', function ($rootScope, log) {
            return {
                link: function link(scope, element) {
                    log.info('Highlighting code');
                    highlight(element);
                }
            };
        }]);

    var highlight = function (elem) {
        require(['highlight'], function () {
            angular.forEach(angular.element(elem)[0].querySelectorAll('code'), function (block) {
                var elem = angular.element(block),
                    parent = elem.parent();
                if (lux.isTag(parent, 'pre')) {
                    root.hljs.highlightBlock(block);
                    parent.addClass('hljs');
                } else {
                    elem.addClass('hljs inline');
                }
            });
            // Handle sphinx highlight
            angular.forEach(angular.element(elem)[0].querySelectorAll('.highlight pre'), function (block) {
                var elem = angular.element(block).addClass('hljs'),
                    div = elem.parent(),
                    p = div.parent();
                if (p.length && p[0].className.substring(0, 10) === 'highlight-')
                    div[0].className = 'language-' + p[0].className.substring(10);
                root.hljs.highlightBlock(block);
            });

        });
    };

});
