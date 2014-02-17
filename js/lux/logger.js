    //
    //  Lux Logger
    //  --------------------

    // Usage:
    //
    //      logger = new Logger();
    //      logger.info('info message')
    var
    log_mapping = {
        'debug': 10,
        'info': 20,
        'warning': 30,
        'error': 40,
        'critical': 50
    },
    //
    default_level = 'info',
    //
    Logger = lux.Logger = Class.extend({
        //
        init: function (opts, parent) {
            var self = this,
                //
                // children for this logger
                children = {},
                //
                // config object
                config = {
                    level: default_level,
                    //
                    formatter: function (msg, level) {
                        return level + ': ' + msg;
                    }
                };

            // Logging shortcut methods
            _(log_mapping).forEach(function (n, level) {
                //
                self[level] = function (msg) {
                    self.log(msg, level);
                };
            });

            _.extend(self, {
                handlers: [],
                //
                config: function (opts) {
                    opts = Object(opts);
                    if (opts.level && log_mapping[opts.level]) {
                        config.level = opts.level;
                    }
                    return config;
                },
                //
                getConfig: function () {
                    return config;
                },
                //
                log: function (msg, level) {
                    var nlevel = log_mapping[level] || 0;
                    if (nlevel > log_mapping[config.level]) {
                        var handlers = self.getHandlers(),
                            hnd;

                        for (var i=0; i<handlers.length; i++) {
                            hnd = handlers[i];
                            if (nlevel >= hnd.nlevel) hnd.log(msg, level);
                        }
                    }
                },
                //
                get: function (name) {
                    var log = children[name];
                    if (!log) {
                        log = new Logger({namespace: name}, self);
                        children[name] = log;
                    }
                    return log;
                },
                //
                getHandlers: function () {
                    if (!self.handlers.length && parent) {
                        return parent.getHandlers();
                    } else {
                        return self.handlers;
                    }
                }
            });
            //
            self.config(opts);
        },
        //
        addHandler: function(options, handler) {
            handler = handler || new LogHandler();
            handler.config(_.extend({}, this.getConfig(), options));
            this.handlers.push(handler);
        }
    }),
    //
    //  Default LogHandler
    //  ---------------------------
    //
    //  Logs messages to the console
    LogHandler = lux.LogHandler = Class.extend({

        config: function (options) {
            _.extend(this, options);
            this.nlevel = log_mapping[this.level] || 0;
        },
        //
        log: function(msg, level) {
            console.log(this.formatter(msg, level));
        }
    }),
    //
    //  HTML LogHandler
    //  ---------------------------
    //
    //  Logs messages to an HTML element
    HtmlHandler = lux.HtmlLogHandler = LogHandler.extend({
        //
        init: function (elem) {
            this.elem = $(elem);
            this.elem.addClass('lux-logger');
        },
        //
        log: function(msg, level) {
            msg = this.formatter(msg, level);
            msg = '<pre class="' + level + '">' + msg + '</pre>';
            this.elem.prepend(msg);
        }
    });
    //
    //  Create the root logger
    var logger = new Logger();
    //
    lux.getLogger = function (namespace, options) {
        var log = logger;
        if (namespace) {
            _.each(namespace.split('.'), function (name) {
                log = log.get(name);
            });
        }
        if (options) {
            log.config(options);
        }
        return log;
    };