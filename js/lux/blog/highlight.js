    //
    //  Code highlighting with highlight.js
    //
    //  This module is added to the blog module so that the highlight
    //  directive can be used
    angular.module('highlight', [])
        .directive('highlight', function () {
            return {
                link: function link(scope, element, attrs) {
                    highlight(element);
                }
            };
        });

    var highlight = function (elem) {
        require(['highlight'], function () {
            $(elem).find('code').each(function(i, block) {
                var elem = $(block),
                    parent = elem.parent();
                if (parent.is('pre')) {
                    root.hljs.highlightBlock(block);
                    parent.addClass('hljs');
                } else {
                    elem.addClass('hljs inline');
                }
            });
        });
    };