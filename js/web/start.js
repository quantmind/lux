define(['jquery', 'lux'], function ($) {
    "use strict";
    //
    // Lux web site manager
    var web = lux.web,
        SKIN_NAMES = ['default', 'primary', 'success', 'inverse', 'error'],
        slice = Array.prototype.slice,
        logger = new lux.utils.Logger();

    logger.addConsole();

    // The logger for the web
    web.logger = logger;

    // Array of skin names
    web.SKIN_NAMES = SKIN_NAMES;

    // Extract a skin information from ``elem``
    web.get_skin = function (elem) {
        if (elem) {
            for (var i=0; i < SKIN_NAMES.length; i++) {
                var name = SKIN_NAMES[i];
                if (elem.hasClass(name)) {
                    return name;
                }
            }
        }
    };
