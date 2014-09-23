    //
    // Code highlighting with highlight.js
    var highlight = function (elem) {
        if (!elem && root.hljs) {
            $('pre code').each(function(i, block) {
                root.hljs.highlightBlock(block);
                $(block).parent().addClass('hljs');
            });
        }
    };

    lux.add_require_callback(highlight);