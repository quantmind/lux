
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
