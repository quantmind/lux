    var
    //
    generateCallbacks = function () {
        var callbackFunctions = [],
            callFunctions = function () {
                var self = this,
                    args = slice.call(arguments, 0);
                callbackFunctions.forEach(function (f) {
                    f.apply(self, args);
                });
            };
        //
        callFunctions.add = function (f) {
            callbackFunctions.push(f);
        };
        return callFunctions;
    },
    //
    // Add a callback for an event to an element
    addEvent = lux.addEvent = function (element, event, callback) {
        var handler = element[event];
        if (!handler)
            element[event] = handler = generateCallbacks();
        if (handler.add)
            handler.add(callback);
    },
    //
    windowResize = lux.windowResize = function (callback) {
        addEvent(window, 'onresize', callback);
    },
    //
    windowHeight = lux.windowHeight = function () {
        return window.innerHeight > 0 ? window.innerHeight : screen.availHeight;
    },
    //
    isAbsolute = new RegExp('^([a-z]+://|//)'),
    //
    isTag = function (element, tag) {
        element = $(element);
        return element.length === 1 && element[0].tagName.toLowerCase() === tag.toLowerCase();
    },
    //
    joinUrl = lux.joinUrl = function (base, url) {
        while (url.substring(0, 1) === '/')
            url = url.substring(1);
        url = '/' + url;
        while (base.substring(base.length-1) === '/')
            base = base.substring(0, base.length-1);
        return base + url;
    };
