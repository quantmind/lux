/* eslint-plugin-disable angular */
/* global define */
define(function () {
    const
        root = window,
        protocol = root.location ? (root.location.protocol === 'file:' ? 'http:' : '') : '',
        ostring = Object.prototype.toString,
        minify = root.minifiedMedia === false ? false : true,
        end = '.js',
        defaultPaths = {
            'ace': '//cdnjs.cloudflare.com/ajax/libs/ace/1.2.3',
            'angular': '//ajax.googleapis.com/ajax/libs/angularjs/1.5.5/angular',
            'angular-animate': '//ajax.googleapis.com/ajax/libs/angularjs/1.5.5/angular-animate',
            'angular-sanitize': '//ajax.googleapis.com/ajax/libs/angularjs/1.5.5/angular-sanitize',
            'angular-touch': '//cdnjs.cloudflare.com/ajax/libs/angular.js/1.5.5/angular-touch',
            'angular-ui-bootstrap': 'https://cdnjs.cloudflare.com/ajax/libs/angular-ui-bootstrap/1.3.2/ui-bootstrap-tpls',
            'angular-ui-router': '//cdnjs.cloudflare.com/ajax/libs/angular-ui-router/0.2.14/angular-ui-router',
            'angular-ui-select': '//cdnjs.cloudflare.com/ajax/libs/angular-ui-select/0.16.1/select',
            'angular-cookies': '//cdnjs.cloudflare.com/ajax/libs/angular.js/1.4.9/angular-cookies',
            'angular-ui-grid': '//cdnjs.cloudflare.com/ajax/libs/angular-ui-grid/3.1.1/ui-grid',
            'angular-scroll': '//cdnjs.cloudflare.com/ajax/libs/angular-scroll/0.7.2/angular-scroll',
            'angular-file-upload': '//cdnjs.cloudflare.com/ajax/libs/danialfarid-angular-file-upload/10.0.2/ng-file-upload',
            'angular-infinite-scroll': '//cdnjs.cloudflare.com/ajax/libs/ngInfiniteScroll/1.2.1/ng-infinite-scroll',
            'angular-moment': '//cdnjs.cloudflare.com/ajax/libs/angular-moment/0.10.1/angular-moment',
            'angular-pusher': '//cdn.jsdelivr.net/angular.pusher/latest/pusher-angular.min.js',
            'videojs': '//vjs.zencdn.net/4.12/video.js',
            'async': '//cdnjs.cloudflare.com/ajax/libs/requirejs-async/0.1.1/async.js',
            'pusher': '//js.pusher.com/2.2/pusher',
            'codemirror': '//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/codemirror',
            'codemirror-markdown': '//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/markdown/markdown',
            'codemirror-javascript': '//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/javascript/javascript',
            'codemirror-python': '//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/python/python.js',
            'codemirror-xml': '//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/xml/xml',
            'codemirror-css': '//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/css/css',
            'codemirror-htmlmixed': '//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/htmlmixed/htmlmixed',
            'crossfilter': '//cdnjs.cloudflare.com/ajax/libs/crossfilter/1.3.12/crossfilter',
            'google-analytics': '//www.google-analytics.com/analytics.js',
            'gridster': '//cdnjs.cloudflare.com/ajax/libs/jquery.gridster/0.5.6/jquery.gridster',
            'holder': '//cdnjs.cloudflare.com/ajax/libs/holder/2.3.1/holder',
            'highlight': '//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.1.0/highlight.min.js',
            'katex': '//cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js',
            'katex-css': '//cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css',
            'leaflet': '//cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/leaflet.js',
            'marked': '//cdnjs.cloudflare.com/ajax/libs/marked/0.3.2/marked',
            'mathjax': '//cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML',
            'moment': '//cdnjs.cloudflare.com/ajax/libs/moment.js/2.10.6/moment',
            'restangular': '//cdnjs.cloudflare.com/ajax/libs/restangular/1.4.0/restangular',
            'sockjs': '//cdnjs.cloudflare.com/ajax/libs/sockjs-client/1.0.3/sockjs',
            'stats': '//cdnjs.cloudflare.com/ajax/libs/stats.js/r11/Stats',
            'topojson': '//cdnjs.cloudflare.com/ajax/libs/topojson/1.6.19/topojson'
        },
        defaultShim = {
            ace: {
                exports: 'ace'
            },
            angular: {
                exports: 'angular'
            },
            'angular-strap-tpl': {
                deps: ['angular', 'angular-strap']
            },
            'google-analytics': {
                exports: root.GoogleAnalyticsObject || 'ga'
            },
            highlight: {
                exports: 'hljs'
            },
            'codemirror': {
                exports: 'CodeMirror'
            },
            'codemirror-htmlmixed': {
                deps: ['codemirror', 'codemirror-xml', 'codemirror-javascript', 'codemirror-css']
            },
            restangular: {
                deps: ['angular']
            },
            crossfilter: {
                exports: 'crossfilter'
            },
            trianglify: {
                deps: ['d3'],
                exports: 'Trianglify'
            },
            mathjax: {
                exports: 'MathJax'
            }
        };

    function config(cfg) {
        cfg.shim = extend(defaultShim, cfg.shim);
        cfg.paths = newPaths(cfg);
        require.config(cfg);
    }

    function newPaths(cfg) {
        var all = {},
            min = minify ? '.min' : '',
            prefix = root.local_require_prefix,
            paths = extend({}, defaultPaths, cfg.paths);

        for (var name in paths) {
            if (paths.hasOwnProperty(name)) {
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
                    if (path.substring(path.length - 3) !== end)
                        path += min;
                    if (params) {
                        if (path.substring(path.length - 3) !== end)
                            path += end;
                        path += '?' + params;
                    }
                    // Add protocol
                    if (path.substring(0, 2) === '//' && protocol)
                        path = protocol + path;

                    if (path.substring(path.length - 3) === end)
                        path = path.substring(0, path.length - 3);
                }
                all[name] = path;
            }
        }
        return all;
    }

    function extend() {
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

    function isObject(value) {
        return ostring.call(value) === '[object Object]';
    }

    return config;
});

