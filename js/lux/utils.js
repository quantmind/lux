    //
    //  Utilities
    //
    var windowResize = lux.windowResize = function (callback, delay) {
        var handle;
        delay = delay ? +delay : 500;

        function execute () {
            handle = null;
            callback();
        }

        $(window).resize(function() {
            if (!handle) {
                handle = setTimeout(execute, delay);
            }
        });
    };

    var isAbsolute = new RegExp('^([a-z]+://|//)');

    var isTag = function (element, tag) {
        element = $(element);
        return element.length === 1 && element[0].tagName.toLowerCase() === tag.toLowerCase();
    };
