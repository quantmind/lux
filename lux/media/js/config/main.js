/* eslint-plugin-disable angular */
define(['lux/config/lux',
        'lux/config/paths',
        'lux/config/shim'], function (lux, defaultPaths, defaultShim) {
    'use strict';

    // If a file assign http as protocol (https does not work with PhantomJS)
    var root = lux.root,
        protocol = root.location ? (root.location.protocol === 'file:' ? 'http:' : '') : '',
        end = '.js';

    // require.config override
    lux.config = function (cfg) {
        cfg = lux.extend(cfg, lux.require);
        if(!cfg.baseUrl) {
            var url = baseUrl();
            if (url !== undefined) cfg.baseUrl = url;
        }
        cfg.shim = lux.extend(defaultShim(root), cfg.shim);
        cfg.paths = newPaths(cfg);
        require.config(cfg);
    };

    return lux;

    function newPaths (cfg) {
        var all = {},
            min = minify() ? '.min' : '',
            prefix = root.local_require_prefix,
            paths = lux.extend(defaultPaths(), cfg.paths);

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

    function baseUrl () {
        if (lux.context)
            return lux.context.MEDIA_URL;
    }

    function minify () {
        if (lux.context)
            return lux.context.MINIFIED_MEDIA;
    }
});

