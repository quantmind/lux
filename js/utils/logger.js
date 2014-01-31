    /**
     * A logger class. Usage:
     * 
     * logger = new Logger();
     */
    lux.utils.Logger = function (level) {
        var handlers = [],
            logger = this,
            log_mapping = {'debug': 10, 'info': 20, 'warning': 30, 'error': 40};
        logger.level = level && log_mapping[level] ? level : 'info';
        //
        function default_formatter(msg, level) {
            return level + ': ' + msg;
        }
        function dummy_log(msg, level) {}
        //
        function log_all(level, msg) {
            for (var i=0; i<handlers.length; ++i) {
                handlers[i].log(msg, level);
            }
        }
        //
        function create_handler(options) {
            options = options || {};
            var slevel = options.level,
                formatter = options.formatter || default_formatter,
                logfunc = options.log || dummy_log,
                nlevel = function () {
                    return log_mapping[slevel ? slevel : logger.level];
                },
                format_message = function (msg, level) {
                    var nl;
                    level = level ? level : 'info';
                    level = level.toLowerCase();
                    nl = log_mapping[level];
                    if (nl !== undefined && nl >= nlevel()) {
                        return {
                            'msg': formatter(msg, level),
                            'level': level
                        };
                    }
                };
            
            if (slevel) {
                slevel = slevel.toLowerCase();
                if (!log_mapping[slevel]) slevel = null;
            }
            
            return {
                level: function () {
                    return slevel ? slevel : logger.level;
                },
                format: format_message,
                log: function(msg, level) {
                    var data = format_message(msg, level);
                    if (data) {
                        logfunc(data);
                    }
                }
            };
        }
        //
        $.each(log_mapping, function(level) {
            logger[level] = function (msg) {
                log_all(level, msg);
            };
        });
        //
        return $.extend(logger, {
            'handlers': handlers,
            addHandler: function(hnd) {
                if(hnd !== undefined && hnd.log !== undefined) {
                    handlers.push(hnd);
                }
            },
            log: function (msg, level) {
                log_all(level, msg);
            },
            addConsole: function(options) {
                if(console !== undefined && console.log !== undefined) {
                    options = options || {};
                    options.log = function(data) {
                        console.log(data.msg);
                    };
                    var console_logger = create_handler(options);
                    logger.addHandler(console_logger);
                    return console_logger;
                }
            },
            addElement: function(html_elem, options) {
                html_elem = $(html_elem);
                if (html_elem.length) {
                    html_elem.addClass('lux-logger');
                    options = $.extend({
                        log: function(data) {
                            var msg = '<pre class="' + data.level + '">' + data.msg + '</pre>';
                            html_elem.prepend(msg);
                        }
                    }, options);
                    var hnd = create_handler(options);
                    hnd.htmlElement = html_elem;
                    logger.addHandler(hnd);
                    return hnd;
                }
            }
        });
    };