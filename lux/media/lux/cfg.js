//
//
(function () {

    if (this.lux)
        this.lux = {};

    // The original require
    var require_config = require.config,
        root = this,
        protocol = root.location ? (root.location.protocol === 'file:' ? 'https:' : '') : '',
        end = '.js',
        processed = false,
        ostring = Object.prototype.toString,
        lux = root.lux;


    function isArray(it) {
        return ostring.call(it) === '[object Array]';
    }

    function minify () {
        if (root.lux.context)
            return lux.context.MINIFIED_MEDIA;
    }

    function baseUrl () {
        if (root.lux.context)
            return lux.context.MEDIA_URL;
    }

    function extend (o1, o2) {
        if (o2) {
            for (var key in o2) {
                if (o2.hasOwnProperty(key))
                    o1[key] = o2[key];
            }
        }
        return o1;
    }

    function defaultPaths () {
        return {};
    }

    // Default shims
    function defaultShims () {
        return {
            angular: {
                exports: "angular"
            },
            "google-analytics": {
                exports: root.GoogleAnalyticsObject || "ga"
            },
            highlight: {
                exports: "hljs"
            },
            lux: {
                deps: ["angular"]
            },
            restangular: {
                deps: ["angular"]
            },
            crossfilter: {
                exports: "crossfilter"
            },
            trianglify: {
                deps: ["d3"],
                exports: "Trianglify"
            },
            mathjax: {
                exports: "MathJax"
            }
        };
    }

    //
    // A function to load module only when angular is ready to compile
    lux.require = function (modules, callback) {
        if (lux.angular || !lux.context.uiRouter) {
            var lazy = {
                callback: callback
            };
            lux.requireQueue.push(lazy);
            require(rcfg.min(modules), function () {
                lazy.arguments = Array.prototype.slice.call(arguments, 0);
            });
        }
    };
    lux.requireQueue = [];
    //
    // Use this function when angular is ready to compile
    lux.loadRequire = function (callback) {
        if (!this.loadingRequire) {
            var queue = this.requireQueue,
                notReady = [];
            this.loadingRequire = true;
            this.requireQueue = notReady;
            for (var i=0; i<queue.length; ++i) {
                if (queue[i].arguments === undefined)
                    notReady.push(queue[i]);
                else
                    queue[i].callback.apply(this.root, queue[i].arguments);
            }
            this.loadingRequire = false;
            if (notReady.length)
                setTimeout(function () {
                    lux.loadRequire(callback);
                });
            else if (callback)
                callback();
        }
    };

    function newPaths (cfg) {
        var all = {},
            min = minify() ? '.min' : '',
            prefix = root.local_require_prefix,
            paths = extend(defaultPaths(), cfg.paths);

        for(var name in paths) {
            if(paths.hasOwnProperty(name)) {
                var path = paths[name];

                if (prefix && path.substring(0, prefix.length) === prefix)
                    path = path.substring(prefix.length);

                if (!cfg.shim[name]) {
                    // Add angular dependency
                    if (name.substring(0, 8) === "angular-")
                        cfg.shim[name] = {
                            deps: ["angular"]
                        };
                    else if (name.substring(0, 3) === "d3-")
                        cfg.shim[name] = {
                            deps: ["d3"]
                        };
                }

                if (typeof(path) !== 'string') {
                    // Don't maanipulate it, live it as it is
                    path = path.url;
                } else {
                    var params = path.split('?');
                    if (params.length === 2) {
                        path = params[0];
                        params = params[1];
                    } else
                        params = '';
                    if (path.substring(path.length-3) !== end)
                        path += min;
                    if (params) {
                        if (path.substring(path.length-3) !== end)
                            path += end;
                        path += '?' + params;
                    }
                    // Add protocol
                    if (path.substring(0, 2) === '//' && protocol)
                        path = protocol + path;

                    if (path.substring(path.length-3) === end)
                        path = path.substring(0, path.length-3);
                }
                all[name] = path;
            }
        }
        return all;
    }

    // require.config override
    require.config = function (cfg) {
        if (!processed) {
            processed = true;
            if(!cfg.baseUrl)
                cfg.baseUrl = baseUrl();
            cfg.shim = extend(defaultShims(), cfg.shim);
            cfg.paths = newPaths(cfg);
            if (!cfg.paths.lux)
                cfg.paths.lux = "lux/lux";
        }
        require_config.call(this, cfg);
    };

    root.newRequire = function () {
        if (arguments.length && isArray(arguments[0]) && minify()) {
            var deps = arguments[0];

            deps.forEach(function (dep, i) {
                if (dep.substring(dep.length-3) !== end)
                    dep += min;
                deps[i] = dep;
            });
        }
        return require.apply(this, arguments);
    };

}());
