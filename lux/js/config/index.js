/* eslint-plugin-disable angular */
define(['lux/config/paths',
        'lux/config/shim'], function (defaultPaths, defaultShim) {
    'use strict';

    // If a file assign http as protocol (https does not work with PhantomJS)
    var root = window,
        protocol = root.location ? (root.location.protocol === 'file:' ? 'http:' : '') : '',
        ostring = Object.prototype.toString,
        minify = root.minifiedMedia === false ? false : true,
        end = '.js';

    return config;

    function config (cfg) {
        cfg.shim = extend(defaultShim(root), cfg.shim);
        cfg.paths = newPaths(cfg);
        require.config(cfg);
    }

    function newPaths (cfg) {
        var all = {},
            min = minify ? '.min' : '',
            prefix = root.local_require_prefix,
            paths = extend(defaultPaths(), cfg.paths);

        for(var name in paths) {
            if(paths.hasOwnProperty(name)) {
                var path = paths[name];

                if (prefix && path.substring(0, prefix.length) === prefix)
                    path = path.substring(prefix.length);

                if (!cfg.shim[name]) {
                    // Add angular dependency
                    if (name.substring(0, 8) === 'angular-')
                        cfg.shim[name] = {
                            deps: ['angular']
                        };
                    else if (name.substring(0, 3) === 'd3-')
                        cfg.shim[name] = {
                            deps: ['d3']
                        };
                    else if (name.substring(0, 11) === 'codemirror-')
                        cfg.shim[name] = {
                            deps: ['codemirror']
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

    function extend () {
        var length = arguments.length,
            object = arguments[0],
            index = 0,
            obj;

        if (!object) object = {};
        while (++index < length) {
            obj = arguments[index];
            if (isObject(obj))
                for (var key in obj) {
                    if (obj.hasOwnProperty(key))
                        object[key] = obj[key];
                }
        }
        return object;
    }

    function isObject (value) {
        return ostring.call(value) === '[object Object]';
    }
});

