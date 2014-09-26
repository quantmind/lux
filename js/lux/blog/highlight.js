    //
    // Code highlighting with highlight.js

    angular.module('highlight', [])
        .directive('highlight', function () {
            return {
                link: function link(scope, element, attrs) {
                    highlight(element);
                }
            };
        });

    var highlight = function (elem) {
        require('highlight', function (hljs) {
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