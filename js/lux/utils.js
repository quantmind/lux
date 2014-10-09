    var generateResize = function () {
        var resizeFunctions = [],
            callResizeFunctions = function () {
                resizeFunctions.forEach(function (f) {
                    f();
                });
            };
        //
        callResizeFunctions.add = function (f) {
            resizeFunctions.push(f);
        };
        return callResizeFunctions;
    };

    //
    //  Utilities
    //
    var windowResize = lux.windowResize = function (callback, delay) {
        var handle;
        delay = delay ? +delay : 0;

        function execute () {
            handle = null;
            callback();
        }

        if (window.onresize === null) {
            window.onresize = generateResize();
        }
        if (window.onresize.add) {
            if (delay) {
                window.onresize.add(function (e) {
                    if (!handle)
                        handle = setTimeout(execute, delay);
                });
            } else {
                window.onresize.add(callback);
            }
        }
    };

    var windowHeight = lux.windowHeight = function () {
        return window.innerHeight > 0 ? window.innerHeight : screen.availHeight;
    };

    var isAbsolute = new RegExp('^([a-z]+://|//)');

    var isTag = function (element, tag) {
        element = $(element);
        return element.length === 1 && element[0].tagName.toLowerCase() === tag.toLowerCase();
    };
