//      Lux Library - v0.4.0

//      Compiled 2016-01-09.
//      Copyright (c) 2016 - Luca Sbardella
//      Licensed BSD.
//      For all details and documentation:
//      http://quantmind.github.io/lux
//
define(['lux/config'], function (lux) {
    'use strict';

    var localRequiredPath = lux.PATH_TO_LOCAL_REQUIRED_FILES || '';

    lux.require.paths = lux.extend(lux.require.paths, {
        'giotto': localRequiredPath + 'luxsite/giotto',
        'angular-img-crop': localRequiredPath + 'luxsite/ng-img-crop.js',
        'angular-infinite-scroll': '//cdnjs.cloudflare.com/ajax/libs/ngInfiniteScroll/1.2.1/ng-infinite-scroll',
        'videojs': '//vjs.zencdn.net/4.12/video.js',
        'moment-timezone': '//cdnjs.cloudflare.com/ajax/libs/moment-timezone/0.4.0/moment-timezone-with-data-2010-2020'
    });

    lux.require.shim = lux.extend(lux.require.shim, {
        'angular-moment': {
            deps: ['angular', 'moment-timezone']
        }
    });

    lux.config();

    return lux;
});

define('lux/config/lux',[], function () {
    "use strict";

    var root = window,
        lux = root.lux || {},
        ostring = Object.prototype.toString;

    if (isString(lux))
        lux = {context: urlBase64DecodeToJSON(lux)};

    root.lux = lux;

    lux.root = root;
    lux.messages = extend(lux.messages);
    lux.require = extend(lux.require);
    lux.extend = extend;
    lux.isString = isString;
    lux.isArray = isArray;
    lux.isObject = isObject;
    lux.urlBase64Decode = urlBase64Decode;
    lux.urlBase64DecodeToJSON = urlBase64DecodeToJSON;

    return lux;

    function extend (o1, o2) {
        if (!o1) o1 = {};
        if (o2) {
            for (var key in o2) {
                if (o2.hasOwnProperty(key))
                    o1[key] = o2[key];
            }
        }
        return o1;
    }

    function isString (value) {
        return ostring.call(value) === '[object String]';
    }

    function isArray (value) {
        return ostring.call(value) === '[object Array]';
    }

    function isObject (value) {
        return ostring.call(value) === '[object Object]';
    }

    function urlBase64Decode (str) {
        var output = str.replace('-', '+').replace('_', '/');
        switch (output.length % 4) {

            case 0: { break; }
        case 2: { output += '=='; break; }
        case 3: { output += '='; break; }
        default: {
                throw 'Illegal base64url string!';
            }
        }
        //polifyll https://github.com/davidchambers/Base64.js
        return decodeURIComponent(escape(window.atob(output)));
    }

    function urlBase64DecodeToJSON (str) {
        var decoded = urlBase64Decode(str);
        if (!decoded) {
            throw new Error('Cannot decode the token');
        }
        return JSON.parse(decoded);
    }

});

define('lux/config/paths',[], function () {

    return function () {
        return {
            "angular": "//ajax.googleapis.com/ajax/libs/angularjs/1.4.7/angular",
            "angular-animate": "//ajax.googleapis.com/ajax/libs/angularjs/1.4.7/angular-animate",
            "angular-mocks": "//ajax.googleapis.com/ajax/libs/angularjs/1.4.7/angular-mocks.js",
            "angular-sanitize": "//ajax.googleapis.com/ajax/libs/angularjs/1.4.7/angular-sanitize",
            "angular-touch": "//cdnjs.cloudflare.com/ajax/libs/angular.js/1.4.7/angular-touch",
            "angular-strap": "//cdnjs.cloudflare.com/ajax/libs/angular-strap/2.2.1/angular-strap",
            "angular-strap-tpl": "//cdnjs.cloudflare.com/ajax/libs/angular-strap/2.2.4/angular-strap.tpl",
            "angular-ui-router": "//cdnjs.cloudflare.com/ajax/libs/angular-ui-router/0.2.14/angular-ui-router",
            "angular-ui-select": "//cdnjs.cloudflare.com/ajax/libs/angular-ui-select/0.12.0/select",
            "angular-cookies": "//cdnjs.cloudflare.com/ajax/libs/angular.js/1.4.4/angular-cookies",
            "angular-ui-grid": "//cdnjs.cloudflare.com/ajax/libs/angular-ui-grid/3.0.7/ui-grid",
            "angular-scroll": "//cdnjs.cloudflare.com/ajax/libs/angular-scroll/0.7.2/angular-scroll",
            "angular-file-upload": "//cdnjs.cloudflare.com/ajax/libs/danialfarid-angular-file-upload/10.0.2/ng-file-upload",
            "angular-moment": "//cdnjs.cloudflare.com/ajax/libs/angular-moment/0.10.1/angular-moment",
            "angular-pusher": "//cdn.jsdelivr.net/angular.pusher/latest/pusher-angular.min.js",
            "videojs": "//vjs.zencdn.net/4.12/video.js",
            "async": "//cdnjs.cloudflare.com/ajax/libs/requirejs-async/0.1.1/async.js",
            "pusher": "//js.pusher.com/2.2/pusher",
            "codemirror": "//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/codemirror",
            "codemirror-markdown": "//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/markdown/markdown",
            "codemirror-javascript": "//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/javascript/javascript",
            "codemirror-python": "//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/python/python.js",
            "codemirror-xml": "//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/xml/xml",
            "codemirror-css": "//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/css/css",
            "codemirror-htmlmixed": "//cdnjs.cloudflare.com/ajax/libs/codemirror/3.21.0/mode/htmlmixed/htmlmixed",
            "crossfilter": "//cdnjs.cloudflare.com/ajax/libs/crossfilter/1.3.11/crossfilter",
            "d3": "//cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3",
            "google-analytics": "//www.google-analytics.com/analytics.js",
            "gridster": "//cdnjs.cloudflare.com/ajax/libs/jquery.gridster/0.5.6/jquery.gridster",
            "holder": "//cdnjs.cloudflare.com/ajax/libs/holder/2.3.1/holder",
            "highlight": "//cdnjs.cloudflare.com/ajax/libs/highlight.js/8.3/highlight.min.js",
            "katex": "//cdnjs.cloudflare.com/ajax/libs/KaTeX/0.3.0/katex.min.js",
            "leaflet": "//cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/leaflet.js",
            "lodash": "//cdnjs.cloudflare.com/ajax/libs/lodash.js/3.10.1/lodash",
            "marked": "//cdnjs.cloudflare.com/ajax/libs/marked/0.3.2/marked",
            "mathjax": "//cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML",
            "moment": "//cdnjs.cloudflare.com/ajax/libs/moment.js/2.10.6/moment",
            "restangular": "//cdnjs.cloudflare.com/ajax/libs/restangular/1.4.0/restangular",
            "sockjs": "//cdnjs.cloudflare.com/ajax/libs/sockjs-client/1.0.3/sockjs",
            "stats": "//cdnjs.cloudflare.com/ajax/libs/stats.js/r11/Stats",
            "topojson": "//cdnjs.cloudflare.com/ajax/libs/topojson/1.6.19/topojson"
        };
    };

});

define('lux/config/shim',[], function () {
    // Default shim
    return function (root) {
        return {
            angular: {
                exports: "angular"
            },
            "angular-strap-tpl": {
                deps: ["angular", "angular-strap"]
            },
            "angular-ui-select": {
                deps: ['angular']
            },
            "google-analytics": {
                exports: root.GoogleAnalyticsObject || "ga"
            },
            highlight: {
                exports: "hljs"
            },
            lux: {
                deps: ["angular", "lodash", "angular-file-upload"]
            },
            "ui-bootstrap": {
                deps: ["angular"]
            },
            "codemirror": {
                exports: "CodeMirror"
            },
            "codemirror-markdown": {
                deps: ["codemirror"]
            },
            "codemirror-xml": {
                deps: ["codemirror"]
            },
            "codemirror-javascript": {
                deps: ["codemirror"]
            },
            "codemirror-python": {
                deps: ["codemirror"]
            },
            "codemirror-css": {
                deps: ["codemirror"]
            },
            "codemirror-htmlmixed": {
                deps: ["codemirror", "codemirror-xml", "codemirror-javascript", "codemirror-css"],
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
    };

});

define('lux/config',['lux/config/lux',
        'lux/config/paths',
        'lux/config/shim'], function (lux, defaultPaths, defaultShim) {

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

    function baseUrl () {
        if (lux.context)
            return lux.context.MEDIA_URL;
    }

    function minify () {
        if (lux.context)
            return lux.context.MINIFIED_MEDIA;
    }
});


define('require.config',['lux/config'], function (lux) {
    'use strict';

    var localRequiredPath = lux.PATH_TO_LOCAL_REQUIRED_FILES || '';

    lux.require.paths = lux.extend(lux.require.paths, {
        'giotto': localRequiredPath + 'luxsite/giotto',
        'angular-img-crop': localRequiredPath + 'luxsite/ng-img-crop.js',
        'angular-infinite-scroll': '//cdnjs.cloudflare.com/ajax/libs/ngInfiniteScroll/1.2.1/ng-infinite-scroll',
        'videojs': '//vjs.zencdn.net/4.12/video.js',
        'moment-timezone': '//cdnjs.cloudflare.com/ajax/libs/moment-timezone/0.4.0/moment-timezone-with-data-2010-2020'
    });

    lux.require.shim = lux.extend(lux.require.shim, {
        'angular-moment': {
            deps: ['angular', 'moment-timezone']
        }
    });

    lux.config();

    return lux;
});

define('lux/utils',['angular', 'lux/config'], function (angular, lux) {
    "use strict";

    var $ = angular.element,
        root = lux.root,
        forEach = angular.forEach,
        slice = Array.prototype.slice,
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
        };
    //
    // Add a callback for an event to an element
    lux.addEvent = function (element, event, callback) {
        var handler = element[event];
        if (!handler)
            element[event] = handler = generateCallbacks();
        if (handler.add)
            handler.add(callback);
    };
    //
    lux.windowResize = function (callback) {
        addEvent(window, 'onresize', callback);
    };
    //
    lux.windowHeight = function () {
        return window.innerHeight > 0 ? window.innerHeight : screen.availHeight;
    };
    //
    lux.isAbsolute = new RegExp('^([a-z]+://|//)');
    //
    // Check if element has tagName tag
    lux.isTag = function (element, tag) {
        element = $(element);
        return element.length === 1 && element[0].tagName === tag.toUpperCase();
    };
    //
    lux.joinUrl = function () {
        var bit, url = '';
        for (var i = 0; i < arguments.length; ++i) {
            bit = arguments[i];
            if (bit) {
                var cbit = bit,
                    slash = false;
                // remove front slashes if cbit has some
                while (url && cbit.substring(0, 1) === '/')
                    cbit = cbit.substring(1);
                // remove end slashes
                while (cbit.substring(cbit.length - 1) === '/') {
                    slash = true;
                    cbit = cbit.substring(0, cbit.length - 1);
                }
                if (cbit) {
                    if (url && url.substring(url.length - 1) !== '/')
                        url += '/';
                    url += cbit;
                    if (slash)
                        url += '/';
                }
            }
        }
        return url;
    };
    //
    //  getOPtions
    //  ===============
    //
    //  Retrive options for the ``options`` string in ``attrs`` if available.
    //  Used by directive when needing to specify options in javascript rather
    //  than html data attributes.
    lux.getOptions = function (attrs) {
        var options;
        if (attrs && typeof attrs.options === 'string') {
            options = getAttribute(root, attrs.options);
            if (typeof options === 'function')
                options = options();
        } else {
            options = {};
        }
        if (lux.isObject(options))
            forEach(attrs, function (value, name) {
                if (name.substring(0, 1) !== '$' && name !== 'options')
                    options[name] = value;
            });
        return options;
    };
    //
    // random generated numbers for a uuid
    lux.s4 = function () {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    };
    //
    // Extend the initial array with values for other arrays
    lux.extendArray = function () {
        if (!arguments.length) return;
        var value = arguments[0],
            push = function (v) {
                value.push(v);
            };
        if (typeof(value.push) === 'function') {
            for (var i = 1; i < arguments.length; ++i)
                forEach(arguments[i], push);
        }
        return value;
    };
    //
    //  querySelector
    //  ===================
    //
    //  Simple wrapper for a querySelector
    lux.querySelector = function (elem, query) {
        elem = $(elem);
        if (elem.length && query)
            return $(elem[0].querySelector(query));
        else
            return elem;
    };
    //
    //    LoadCss
    //  =======================
    //
    //  Load a style sheet link
    var loadedCss = {};
    //
    lux.loadCss = function (filename) {
        if (!loadedCss[filename]) {
            loadedCss[filename] = true;
            var fileref = document.createElement("link");
            fileref.setAttribute("rel", "stylesheet");
            fileref.setAttribute("type", "text/css");
            fileref.setAttribute("href", filename);
            document.getElementsByTagName("head")[0].appendChild(fileref);
        }
    };
    //
    //
    lux.globalEval = function (data) {
        if (data) {
            // We use execScript on Internet Explorer
            // We use an anonymous function so that context is window
            // rather than jQuery in Firefox
            (root.execScript || function (data) {
                root["eval"].call(root, data);
            })(data);
        }
    };
    //
    // Simple Slugify function
    lux.slugify = function (str) {
        str = str.replace(/^\s+|\s+$/g, ''); // trim
        str = str.toLowerCase();

        // remove accents, swap ñ for n, etc
        var from = "àáäâèéëêìíïîòóöôùúüûñç·/_,:;";
        var to = "aaaaeeeeiiiioooouuuunc------";
        for (var i = 0, l = from.length; i < l; i++) {
            str = str.replace(new RegExp(from.charAt(i), 'g'), to.charAt(i));
        }

        str = str.replace(/[^a-z0-9 -]/g, '') // remove invalid chars
            .replace(/\s+/g, '-') // collapse whitespace and replace by -
            .replace(/-+/g, '-'); // collapse dashes

        return str;
    };
    //
    lux.now = function () {
        return Date.now ? Date.now() : new Date().getTime();
    };
//
    lux.size = function (o) {
        if (!o) return 0;
        if (o.length !== undefined) return o.length;
        var n = 0;
        forEach(o, function () {
            ++n;
        });
        return n;
    };
    //
    // Used by the getObject function
    function getAttribute (obj, name) {
        var bits = name.split('.');

        for (var i = 0; i < bits.length; ++i) {
            obj = obj[bits[i]];
            if (!obj) break;
        }
        if (typeof obj === 'function')
            obj = obj();

        return obj;
    }
    //
    //
    //  Get Options
    //  ==============================================
    //
    //  Obtain an object from scope (if available) with fallback to
    //  the global javascript object
    lux.getObject = function (attrs, name, scope) {
        var key = attrs[name],
            exclude = [name, 'class', 'style'],
            options;

        if (key) {
            // Try the scope first
            if (scope) options = getAttribute(scope, key);

            if (!options) options = getAttribute(root, key);
        }
        if (!options) options = {};

        forEach(attrs, function (value, name) {
            if (name.substring(0, 1) !== '$' && exclude.indexOf(name) === -1)
                options[name] = value;
        });
        return options;
    };

    /**
     * Formats a string (using simple substitution)
     * @param   {String}    str         e.g. "Hello {name}!"
     * @param   {Object}    values      e.g. {name: "King George III"}
     * @returns {String}                e.g. "Hello King George III!"
     */
    lux.formatString = function (str, values) {
        return str.replace(/{(\w+)}/g, function (match, placeholder) {
            return values.hasOwnProperty(placeholder) ? values[placeholder] : '';
        });
    };
    //
    //  Capitalize the first letter of string
    lux.capitalize = function (str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    };

    /**
     * Obtain a JSON object from a string (if available) otherwise null
     *
     * @param {string}
     * @returns {object} json object
     */
    lux.getJsonOrNone = function (str) {
        try {
            return JSON.parse(str);
        } catch (error) {
            return null;
        }
    };

    /**
     * Checks if a JSON value can be stringify
     *
     * @param {value} json value
     * @returns {boolean}
     */
    lux.isJsonStringify = function (value) {
        if (lux.isObject(value) || lux.isArray(value) || lux.isString(value))
            return true;
        return false;
    };

    return lux;
});

define('lux/services/api',['angular', 'lux/config'], function (angular, lux) {
    "use strict";

    var $ = angular.element,
        extend = angular.extend;

    lux.messages.no_api = function (url) {
        return {
            text: 'Api client for "' + url + '" is not available',
            icon: 'fa fa-exclamation-triangle'
        };
    };

    //  Lux Api service
    //	===================
    //
    //	A factory of javascript clients to web services
    angular.module('lux.services', [])
        //
        .value('ApiTypes', {})
        //
        .value('AuthApis', {})
        //
        .run(['$lux', function ($lux) {
            //
            var name = $(document.querySelector("meta[name=csrf-param]")).attr('content'),
                csrf_token = $(document.querySelector("meta[name=csrf-token]")).attr('content');

            $lux.user_token = $(document.querySelector("meta[name=user-token]")).attr('content');

            if (name && csrf_token) {
                $lux.csrf = {};
                $lux.csrf[name] = csrf_token;
            }
        }])
        //
        .service('$lux', ['$location', '$window', '$q', '$http', '$log',
            '$timeout', 'ApiTypes', 'AuthApis', '$templateCache',
            '$compile',
            function ($location, $window, $q, $http, $log, $timeout,
                      ApiTypes, AuthApis, $templateCache, $compile) {
                var $lux = this;

                this.location = $location;
                this.window = $window;
                this.log = $log;
                this.http = $http;
                this.q = $q;
                this.timeout = $timeout;
                this.apiUrls = {};
                this.$log = $log;
                this.messages = extend({}, lux.messageService, {
                    pushMessage: function (message) {
                        this.log($log, message);
                    }
                });
                //  Create a client api
                //  -------------------------
                //
                //  context: an api name or an object containing, name, url and type.
                //
                //  name: the api name
                //  url: the api base url
                //  type: optional api type (default is ``lux``)
                this.api = function (url, api) {
                    if (arguments.length === 1) {
                        var defaults;
                        if (isObject(url)) {
                            defaults = url;
                            url = url.url;
                        }
                        api = ApiTypes[url];
                        if (!api)
                            $lux.messages.error(lux.messages.no_api(url));
                        else
                            return api(url, this).defaults(defaults);
                    } else if (arguments.length === 2) {
                        ApiTypes[url] = api;
                        return api(url, this);
                    }
                };

                // Set/get the authentication handler for a given api
                this.authApi = function (api, auth) {
                    if (arguments.length === 1)
                        return AuthApis[api.baseUrl()];
                    else if (arguments.length === 2)
                        AuthApis[api.baseUrl()] = auth;
                };

                //
                // Change the form data depending on content type
                this.formData = function (contentType) {

                    return function (data) {
                        data = extend(data || {}, $lux.csrf);
                        if (contentType === 'application/x-www-form-urlencoded')
                            return $.param(data);
                        else if (contentType === 'multipart/form-data') {
                            var fd = new FormData();
                            forEach(data, function (value, key) {
                                fd.append(key, value);
                            });
                            return fd;
                        } else {
                            return JSON.stringify(data);
                        }
                    };
                };
                //
                // Render a template from a url
                this.renderTemplate = function (url, element, scope, callback) {
                    var template = $templateCache.get(url);
                    if (!template) {
                        $http.get(url).then(function (resp) {
                            template = resp.data;
                            $templateCache.put(url, template);
                            _render(element, template, scope, callback);
                        }, function (resp) {
                            $lux.messages.error('Could not load template from ' + url);
                        });
                    } else
                        _render(element, template, scope, callback);
                };

                function _render(element, template, scope, callback) {
                    var elem = $compile(template)(scope);
                    element.append(elem);
                    if (callback) callback(elem);
                }
            }]);
    //
    function wrapPromise(promise) {

        promise.success = function (fn) {

            return wrapPromise(this.then(function (response) {
                var r = fn(response.data, response.status, response.headers);
                return r === undefined ? response : r;
            }));
        };

        promise.error = function (fn) {

            return wrapPromise(this.then(null, function (response) {
                var r = fn(response.data, response.status, response.headers);
                return r === undefined ? response : r;
            }));
        };

        return promise;
    }

    var ENCODE_URL_METHODS = ['delete', 'get', 'head', 'options'];
    //
    //  Lux API Interface for REST
    //
    lux.apiFactory = function (url, $lux) {
        //
        //  Object containing the urls for the api.
        var api = {},
            defaults = {};

        api.toString = function () {
            if (defaults.name)
                return joinUrl(api.baseUrl(), defaults.name);
            else
                return api.baseUrl();
        };
        //
        // Get/Set defaults options for requests
        api.defaults = function (_) {
            if (!arguments.length) return defaults;
            if (_)
                defaults = _;
            return api;
        };

        api.formReady = function (model, formScope) {
            $ux.log.error('Cannot handle form ready');
        };
        //
        // API base url
        api.baseUrl = function () {
            return url;
        };
        //
        api.get = function (opts, data) {
            return api.request('get', opts, data);
        };
        //
        api.post = function (opts, data) {
            return api.request('post', opts, data);
        };
        //
        api.put = function (opts, data) {
            return api.request('put', opts, data);
        };
        //
        api.head = function (opts, data) {
            return api.request('head', opts, data);
        };
        //
        api.delete = function (opts, data) {
            return api.request('delete', opts, data);
        };
        //
        //  Add additional Http options to the request
        api.httpOptions = function (request) {
        };
        //
        //  This function can be used to add authentication
        api.authentication = function (request) {
        };
        //
        //  Return the current user
        //  ---------------------------
        //
        //  Only implemented by apis managing authentication
        api.user = function () {
        };
        //
        // Perform the actual request and return a promise
        //	method: HTTP method
        //  opts: request options to override defaults
        //	data: body or url data
        api.request = function (method, opts, data) {
            // handle urlparams when not an object
            var o = extend({}, api.defaults());
            o.method = method.toLowerCase();
            if (ENCODE_URL_METHODS.indexOf(o.method) === -1) {
                o.data = data;
            } else {
                if (!isObject(o.params)) {
                    o.params = {};
                }
                extend(o.params, data || {});
            }

            opts = extend(o, opts);

            var d = $lux.q.defer(),
            //
                request = extend({
                    name: opts.name,
                    //
                    deferred: d,
                    //
                    on: wrapPromise(d.promise),
                    //
                    options: opts,
                    //
                    error: function (response) {
                        if (isString(response.data))
                            response.data = {error: true, message: data};
                        d.reject(response);
                    },
                    //
                    success: function (response) {
                        if (isString(response.data))
                            response.data = {message: data};

                        if (!response.data || response.data.error)
                            d.reject(response);
                        else
                            d.resolve(response);
                    }
                });
            //
            delete opts.name;
            if (opts.url === api.baseUrl())
                delete opts.url;
            //
            api.call(request);
            //
            return request.on;
        };

        /**
         * Populates $lux.apiUrls for an API URL.
         *
         * @returns      promise
         */
        api.populateApiUrls = function () {
            $lux.log.info('Fetching api info');
            return $lux.http.get(url).then(function (resp) {
                $lux.apiUrls[url] = resp.data;
                return resp.data;
            });
        };

        /**
         * Gets API endpoint URLs from root URL
         *
         * @returns     promise, resolved when API URLs available
         */
        api.getApiNames = function () {
            var promise, deferred;
            if (!angular.isObject($lux.apiUrls[url])) {
                promise = api.populateApiUrls();
            } else {
                deferred = $lux.q.defer();
                promise = deferred.promise;
                deferred.resolve($lux.apiUrls[url]);
            }
            return promise;
        };

        /**
         * Gets the URL for an API target
         *
         * @param target
         * @returns     promise, resolved when the URL is available
         */
        api.getUrlForTarget = function (target) {
            return api.getApiNames().then(function (apiUrls) {
                var url = apiUrls[target.name];
                if (target.path) {
                    url = joinUrl(url, target.path);
                }
                return url;
            });
        };

        //
        //  Execute an API call for a given request
        //  This method is hardly used directly,
        //	the ``request`` method is normally used.
        //
        //      request: a request object obtained from the ``request`` method
        api.call = function (request) {
            //
            if (!request.baseUrl && request.name) {
                var apiUrls = $lux.apiUrls[url];

                if (apiUrls) {
                    request.baseUrl = apiUrls[request.name];
                    //
                    // No api url!
                    if (!request.baseUrl)
                        return request.error('Could not find a valid url for ' + request.name);

                    //
                } else {
                    // Fetch the api urls
                    return api.populateApiUrls(url).then(function () {
                        api.call(request);
                    }, request.error);
                    //
                }
            }

            if (!request.baseUrl)
                request.baseUrl = api.baseUrl();

            var opts = request.options;

            if (!opts.url) {
                var href = request.baseUrl;
                if (opts.path)
                    href = joinUrl(request.baseUrl, opts.path);
                opts.url = href;
            }

            api.httpOptions(request);

            //
            // Fetch authentication token?
            var r = api.authentication(request);
            if (r) return r;
            //
            var options = request.options;

            if (options.url) {
                $lux.log.info('Executing HTTP ' + options.method + ' request @ ' + options.url);
                $lux.http(options).then(request.success, request.error);
            }
            else
                request.error('Api url not available');
        };

        return api;
    };

    return lux.apiFactory;
});

define('lux/services/luxweb',['angular', 'lux/config', 'lux/services/api'], function (angular, lux, apiFactory) {
    "use strict";
    //
    //	LUX WEB API
    //	===================
    //
    //  Angular module for interacting with lux-based WEB APIs
    angular.module('lux.webapi', ['lux.services'])

        .run(['$rootScope', '$lux', function ($scope, $lux) {
            //
            if ($scope.API_URL) {
                $lux.api($scope.API_URL, luxweb).scopeApi($scope);
            }
        }]);

    //
    //	Decode JWT
    //	================
    //
    //	Decode a JASON Web Token and return the decoded object
    lux.decodeJWToken = function (token) {
        var parts = token.split('.');

        if (parts.length !== 3) {
            throw new Error('JWT must have 3 parts');
        }

        return lux.urlBase64DecodeToJSON(parts[1]);
    };

    var //
    //  HTTP verbs which don't send a csrf token in their requests
        CSRFset = ['get', 'head', 'options'],
    //
        luxweb = function (url, $lux) {

            var api = apiFactory(url, $lux),
                request = api.request,
                auth_name = 'authorizations_url',
                web;

            // Set the name of the authentication endpoints
            api.authName = function (name) {
                if (arguments.length === 1) {
                    auth_name = name;
                    return api;
                } else
                    return auth_name;
            };

            // Set/Get the user token
            api.token = function (token) {
                return $lux.user_token;
            };

            // Perform Logout
            api.logout = function (scope) {
                var auth = $lux.authApi(api);
                if (!auth) {
                    $lux.messages.error('Error while logging out');
                    return;
                }
                scope.$emit('pre-logout');
                auth.post({
                    name: auth.authName(),
                    path: lux.context.LOGOUT_URL
                }).then(function () {
                    scope.$emit('after-logout');
                    if (lux.context.POST_LOGOUT_URL) {
                        $lux.window.location.href = lux.context.POST_LOGOUT_URL;
                    } else {
                        $lux.window.location.reload();
                    }
                }, function (response) {
                    $lux.messages.error('Error while logging out');
                });
            };

            // Get the user from the JWT
            api.user = function () {
                var token = api.token();
                if (token) {
                    var u = lux.decodeJWToken(token);
                    u.token = token;
                    return u;
                }
            };

            // Redirect to the LOGIN_URL
            api.login = function () {
                if (lux.context.LOGIN_URL) {
                    $lux.window.location.href = lux.context.LOGIN_URL;
                    $lux.window.reload();
                }
            };

            //
            //  Fired when a lux form uses this api to post data
            //
            //  Check the run method in the "lux.services" module for more information
            api.formReady = function (model, formScope) {
                var resolve = api.defaults().get;
                if (resolve) {
                    api.get().success(function (data) {
                        forEach(data, function (value, key) {
                            // TODO: do we need a callback for JSON fields?
                            // or shall we leave it here?

                            var modelType = formScope[formScope.formModelName + 'Type'];
                            var jsonArrayKey = key.split('[]')[0];

                            // Stringify json only if has json mode enabled
                            if (modelType[jsonArrayKey] === 'json' && isJsonStringify(value)) {

                                // Get rid of the brackets from the json array field
                                if (isArray(value)) {
                                    key = jsonArrayKey;
                                }

                                value = JSON.stringify(value, null, 4);
                            }

                            if (isArray(value)) {
                                model[key] = [];
                                forEach(value, function (item) {
                                    model[key].push(item.id || item);
                                });
                            } else {
                                model[key] = value.id || value;
                            }
                        });
                    });
                }
            };

            //  override request and attach error callbacks
            api.request = function (method, opts, data) {
                var promise = request.call(api, method, opts, data);
                promise.error(function (data, status) {
                    if (status === 401)
                        api.login();
                    else if (!status)
                        $lux.log.error('Server down, could not complete request');
                    else if (status === 404)
                        $lux.log.info('Endpoint not found' + ((opts.path) ? ' @ ' + opts.path : ''));
                });
                return promise;
            };

            api.httpOptions = function (request) {
                var options = request.options;

                if ($lux.csrf && CSRFset.indexOf(options.method === -1)) {
                    options.data = extend(options.data || {}, $lux.csrf);
                }

                if (!options.headers)
                    options.headers = {};
                options.headers['Content-Type'] = 'application/json';
            };

            //
            // Initialise a scope with an auth api handler
            api.scopeApi = function (scope, auth) {
                //  Get the api client
                if (auth) {
                    // Register auth as the authentication client of this api
                    $lux.authApi(api, auth);
                    auth.authName(null);
                }

                scope.api = function () {
                    return $lux.api(url);
                };

                //  Get the current user
                scope.getUser = function () {
                    return api.user();
                };

                //  Logout the current user
                scope.logout = function (e) {
                    if (e && e.preventDefault) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                    if (api.user()) api.logout(scope);
                };
            };

            return api;
        };

    return luxweb;
});

define('lux/services/luxrest',['angular', 'lux/config', 'lux/services/luxweb'], function (angular, lux, luxWebApi) {
    "use strict";
    //
    //	Angular Module for JS clients of Lux Rest APIs
    //	====================================================
    //
    //	If the ``API_URL`` is defined at root scope, register the
    //	javascript client with the $lux service and add functions to the root
    //	scope to retrieve the api client handler and user informations
    angular.module('lux.restApi', ['lux.services'])

        .run(['$rootScope', '$lux', function ($scope, $lux) {

            // If the root scope has an API_URL register the luxrest client
            if ($scope.API_URL) {
                //
                // web api handler
                var web = $lux.api('', luxWebApi);
                // rest api handler
                $lux.api($scope.API_URL, luxrest).scopeApi($scope, web);
            }

        }]);

    //
    //  API handler for lux rest api
    //
    //  This handler connects to lux-based rest apis and
    //
    //  * Perform authentication using username/email & password
    //  * After authentication a JWT is received and stored in the localStorage or sessionStorage
    //  * Optional second factor authentication
    //  --------------------------------------------------
    var luxrest = function (url, $lux) {

        var api = luxWebApi(url, $lux);

        api.httpOptions = function (request) {
            var options = request.options,
                headers = options.headers;
            if (!headers)
                options.headers = headers = {};
            headers['Content-Type'] = 'application/json';
        };

        // Add authentication token if available
        api.authentication = function (request) {
            //
            // If the call is for the authorizations_url api, add callback to store the token
            if (request.name === 'authorizations_url' &&
                request.options.url === request.baseUrl &&
                request.options.method === 'post') {

                request.on.success(function (data, status) {
                    // reload the Page
                    $lux.window.location.reload();
                    //api.token(data.token);
                });

            } else {
                var jwt = api.token();

                if (jwt) {
                    var headers = request.options.headers;
                    if (!headers)
                        request.options.headers = headers = {};

                    headers.Authorization = 'Bearer ' + jwt;
                }
            }
        };

        return api;
    };

    return luxrest;

});

define('lux/services/ws',['angular', 'lux/config'], function (angular, lux) {
    "use strict";

    //
    // Websocket handler for RPC and pub/sub messages
    function sockJs(url, websockets, websocketChannels, log) {
        var handler = {},
            context = websockets[url];

        if (!context) {
            context = {
                executed: {},
                id: 0
            };

            websockets[url] = context;
        }

        handler.getUrl = function () {
            return url;
        };

        // RPC call
        //
        //  method: rpc method to call
        //  data: optional object with rpc parameters
        //  callback: optional callback invoked when a response is received
        handler.rpc = function (method, data, callback) {
            data = {
                method: method,
                id: ++context.id,
                data: data
            };
            var msg = JSON.stringify(data);
            if (callback) {
                context.executed[data.id] = callback;
            }
            return handler.sendMessage(msg);
        };

        handler.connect = function (onopen) {
            var sock = context.sock;

            if (angular.isArray(sock)) {
                if (onopen) sock.push(onopen);
            }
            else if (sock) {
                if (onopen) onopen(sock);
            } else {
                sock = [];
                context.sock = sock;
                if (onopen) sock.push(onopen);

                require(['sockjs'], function (SockJs) {
                    var sock = new SockJs(url);

                    sock.onopen = function () {
                        var callbacks = context.sock;
                        context.sock = sock;
                        log.info('New web socket connection with ' + url);
                        callbacks.forEach(function (cbk) {
                            cbk(sock);
                        });
                    };

                    sock.onmessage = function (e) {
                        var msg = angular.fromJson(e.data),
                            listeners;
                        if (msg.event)
                            log.info('event', msg.event);
                        if (msg.channel)
                            listeners = websocketChannels[msg.channel];
                        if (msg.data)
                            msg.data = angular.fromJson(msg.data);
                        if (msg.channel === 'rpc') {
                            if (typeof msg.data.id !== 'undefined') {
                                if (context.executed[msg.data.id]) {
                                    context.executed[msg.data.id](msg.data.data, sock);
                                    if (msg.data.rpcComplete) {
                                        delete context.executed[msg.data.id];
                                    }
                                }
                            }
                        } else {
                            angular.forEach(listeners, function (listener) {
                                listener(sock, msg);
                            });
                        }

                    };

                    sock.onclose = function () {
                        delete websockets[url];
                        log.warn('Connection with ' + url + ' CLOSED');
                    };
                });
            }
            return handler;
        };

        handler.sendMessage = function (msg, forceEncode) {
            return handler.connect(function (sock) {
                if (typeof msg !== 'string' || forceEncode) {
                    msg = JSON.stringify(msg);
                }
                sock.send(msg);
            });
        };

        handler.disconnect = function () {
            var sock = context.sock;

            if (angular.isArray(sock))
                sock.push(function (s) {
                    s.close();
                });
            else if (sock)
                sock.close();
            return handler;
        };

        handler.addListener = function (channel, callback) {
            var callbacks = websocketChannels[channel];
            if (!callbacks) {
                callbacks = [];
                websocketChannels[channel] = callbacks;
            }
            callbacks.push(callback);
        };

        return handler;
    }

    //
    //  Sock module
    //  ==================
    //
    //
    //
    angular.module('lux.sockjs', [])

        .run(['$rootScope', '$log', function (scope, log) {

            var websockets = {},
                websocketChannels = {};

            scope.sockJs = function (url) {
                return sockJs(url, websockets, websocketChannels, log);
            };

        }]);

});

define('lux/services',['lux/services/luxweb',
        'lux/services/luxrest',
        'lux/services/ws'], function () {
    "use strict";
});

define('lux',['angular', 'lux/utils', 'lux/services'], function(angular, lux) {
    "use strict";

    var forEach = angular.forEach,
        extend = angular.extend,
        angular_bootstrapped = false,
        $ = angular.element,
        defaults = {
            url: '',    // base url for the web site
            MEDIA_URL: '',  // default url for media content
            hashPrefix: '',
            ngModules: []
        };

    //
    lux.version = '0.1.0';
    lux.forEach = angular.forEach;
    lux.context = extend({}, defaults, lux.context);

    lux.media = function (url, ctx) {
        if (!ctx)
            ctx = lux.context;
        return lux.joinUrl(ctx.url, ctx.MEDIA_URL, url);
    };

    lux.loader = angular.module('lux.loader', [])
    	//
        .value('context', lux.context)
        //
        .config(['$controllerProvider', function ($controllerProvider) {
            lux.loader.cp = $controllerProvider;
            lux.loader.controller = $controllerProvider;
        }])
        //
        .run(['$rootScope', '$log', '$timeout', 'context',
              	function (scope, $log, $timeout, context) {
            $log.info('Extend root scope with context');
            extend(scope, context);
            scope.$timeout = $timeout;
            scope.$log = $log;
        }]);
    //
    //  Bootstrap the document
    //  ============================
    //
    //  * ``name``  name of the module
    //  * ``modules`` modules to include
    //
    //  These modules are appended to the modules available in the
    //  lux context object and therefore they will be processed afterwards.
    //
    lux.bootstrap = function (name, modules) {
        //
        // actual bootstrapping function
        function _bootstrap() {
            //
            // Resolve modules to load
            var mods = lux.context.ngModules;
            if(!mods) mods = [];

            // Add all modules from input
            forEach(modules, function (mod) {
                mods.push(mod);
            });
            // Insert the lux loader as first module
            mods.splice(0, 0, 'lux.loader');
            angular.module(name, mods);
            angular.bootstrap(document, [name]);
        }

        if (!angular_bootstrapped) {
            angular_bootstrapped = true;
            //
            $(document).ready(function() {
                _bootstrap();
            });
        }
    };

    return lux;
});

define('lux/forms/utils',['angular',
        'lux'], function (angular, lux) {
    "use strict";

    angular.module('lux.form.utils', ['lux.pagination'])

        .constant('lazyLoadOffset', 40) // API will be called this number of pixels
                                        // before bottom of UIselect list

        .directive('remoteOptions', ['$lux', 'luxPaginationFactory', 'lazyLoadOffset', '$timeout', function ($lux, LuxPagination, lazyLoadOffset, $timeout) {

            function remoteOptions(luxPag, target, scope, attrs, element) {

                function lazyLoad(e) {
                    // lazyLoad requests the next page of data from the API
                    // when nearing the bottom of a <select> list
                    var uiSelect = element[0].querySelector('.ui-select-choices');

                    e.stopPropagation();
                    if (!uiSelect) return;

                    var uiSelectChild = uiSelect.querySelector('.ui-select-choices-group');
                    uiSelect = angular.element(uiSelect);

                    uiSelect.on('scroll', function() {
                        var offset = uiSelectChild.clientHeight - this.clientHeight - lazyLoadOffset;

                        if (this.scrollTop > offset) {
                            uiSelect.off();
                            luxPag.loadMore();
                        }
                    });

                }

                function enableSearch() {
                    if (searchInput.data().onKeyUp) return;

                    searchInput.data('onKeyUp', true);
                    searchInput.on('keyup', function(e) {
                        var query = e.srcElement.value;
                        var searchField = attrs.remoteOptionsId === 'id' ? nameOpts.source : attrs.remoteOptionsId;

                        cleanSearchResults();

                        // Only call API with search if query is > 3 chars
                        if (query.length > 3) {
                            luxPag.search(query, searchField);
                        }
                    });
                }

                function loopAndPush(data) {
                    angular.forEach(data.data.result, function (val) {
                        var name;
                        if (nameFromFormat) {
                            name = formatString(nameOpts.source, val);
                        } else {
                            name = val[nameOpts.source];
                        }

                        options.push({
                            id: val[id],
                            name: name,
                            searched: data.searched ? true : false
                        });
                    });

                    cleanDuplicates();
                }

                function cleanSearchResults() {
                    // options objects containing data.searched will be removed
                    // after relevant search.
                    for (var i = 0; i<options.length; i++) {
                        if (options[i].searched) options.splice(i, 1);
                    }
                }

                function cleanDuplicates() {
                    // $timeout waits for rootScope.$digest to finish,
                    // then removes duplicates from options list on the next tick.
                    $timeout(function() {
                        return scope.$select.selected;
                    }).then(function(selected) {
                        for (var a=0; a<options.length; a++) {
                            for (var b=0; b<selected.length; b++) {
                                if(options[a].id === selected[b].id) options.splice(a, 1);
                            }
                        }
                    });
                }

                function buildSelect(data) {
                    // buildSelect uses data from the API to populate
                    // the options variable, which builds our <select> list
                    if (data.data && data.data.error) {
                        options.splice(0, 1, {id: 'placeholder', name: 'Unable to load data...'});
                        throw new Error(data.data.message);
                    } else {
                        loopAndPush(data);
                    }
                }

                var id = attrs.remoteOptionsId || 'id';
                var nameOpts = attrs.remoteOptionsValue ? JSON.parse(attrs.remoteOptionsValue) : {
                        type: 'field',
                        source: 'id'
                    };
                var nameFromFormat = nameOpts.type === 'formatString';
                var initialValue = {};
                var params = JSON.parse(attrs.remoteOptionsParams || '{}');
                var options = [];
                var searchInput = angular.element(element[0].querySelector('input[type=text]'));

                scope[target.name] = options;

                initialValue.id = '';
                initialValue.name = 'Loading...';

                options.push(initialValue);

                // Set empty value if field was not filled
                if (scope[scope.formModelName][attrs.name] === undefined) {
                    scope[scope.formModelName][attrs.name] = '';
                }

                if (attrs.multiple) {
                    // Increasing default API call limit as UISelect multiple
                    // displays all preselected options
                    params.limit = 200;
                    params.sortby = nameOpts.source ? nameOpts.source + ':asc' : 'id:asc';
                    options.splice(0, 1);
                } else {
                    params.sortby = params.sortby ? params.sortby + ':asc' : 'id:asc';
                    // Options with id 'placeholder' are disabled in
                    // forms.js so users can't select them
                    options[0] = {
                        name: 'Please select...',
                        id: 'placeholder'
                    };
                }

                // Use LuxPagination's getData method to call the api
                // with relevant parameters and pass in buildSelect as callback
                luxPag.getData(params, buildSelect);
                // Listen for LuxPagination to emit 'moreData' then run
                // lazyLoad and enableSearch
                scope.$on('moreData', function(e) {
                    lazyLoad(e);
                    enableSearch();
                });
            }

            function link(scope, element, attrs) {

                if (attrs.remoteOptions) {
                    var target = JSON.parse(attrs.remoteOptions);
                    var luxPag = new LuxPagination(scope, target, attrs.multiple ? true : false);

                    if (luxPag && target.name)
                        return remoteOptions(luxPag, target, scope, attrs, element);
                }

                // TODO: message
            }

            return {
                link: link
            };
        }])

        .directive('selectOnClick', function () {
            return {
                restrict: 'A',
                link: function (scope, element, attrs) {
                    element.on('click', function () {
                        if (!window.getSelection().toString()) {
                            // Required for mobile Safari
                            this.setSelectionRange(0, this.value.length);
                        }
                    });
                }
            };
        });

});

define('lux/forms/handlers',['angular', 'lux'], function (angular, lux) {
    "use strict";

    angular.module('lux.form.handlers', ['lux.services'])

        .run(['$lux', function ($lux) {
            var formHandlers = {};
            $lux.formHandlers = formHandlers;

            formHandlers.reload = function () {
                $lux.window.location.reload();
            };

            formHandlers.redirectHome = function (response, scope) {
                var href = scope.formAttrs.redirectTo || '/';
                $lux.window.location.href = href;
            };

            // response handler for login form
            formHandlers.login = function (response, scope) {
                var target = scope.formAttrs.action,
                    api = $lux.api(target);
                if (api)
                    api.token(response.data.token);
                $lux.window.location.href = lux.context.POST_LOGIN_URL || lux.context.LOGIN_URL;
            };

            //
            formHandlers.passwordRecovery = function (response, scope) {
                var email = response.data.email;
                if (email) {
                    var text = "We have sent an email to <strong>" + email + "</strong>. Please follow the instructions to change your password.";
                    $lux.messages.success(text);
                }
                else
                    $lux.messages.error("Could not find that email");
            };

            //
            formHandlers.signUp = function (response, scope) {
                var email = response.data.email;
                if (email) {
                    var text = "We have sent an email to <strong>" + email + "</strong>. Please follow the instructions to confirm your email.";
                    $lux.messages.success(text);
                }
                else
                    $lux.messages.error("Something wrong, please contact the administrator");
            };

            //
            formHandlers.passwordChanged = function (response, scope) {
                if (response.data.success) {
                    var text = 'Password succesfully changed. You can now <a title="login" href="' + lux.context.LOGIN_URL + '">login</a> again.';
                    $lux.messages.success(text);
                } else
                    $lux.messages.error('Could not change password');
            };

            formHandlers.enquiry = function (response, scope) {
                if (response.data.success) {
                    var text = 'Thank you for your feedback!';
                    $lux.messages.success(text);
                } else
                    $lux.messages.error('Feedback form error');
            };

        }]);

});

define('lux/forms/process',['angular',
        'lux',
        'lux/forms/handlers'], function (angular, lux) {
    "use strict";

    angular.module('lux.form.process', ['ngFileUpload'])
        .run(['$lux', 'Upload', function ($lux, Upload) {

            //
            //	Form processor
            //	=========================
            //
            //	Default Form processing function
            // 	If a submit element (input.submit or button) does not specify
            // 	a ``click`` entry, this function is used
            //
            //  Post Result
            //  -------------------
            //
            //  When a form is processed succesfully, this method will check if the
            //  ``formAttrs`` object contains a ``resultHandler`` parameter which should be
            //  a string.
            //
            //  In the event the ``resultHandler`` exists,
            //  the ``$lux.formHandlers`` object is checked if it contains a function
            //  at the ``resultHandler`` value. If it does, the function is called.
            lux.processForm = function (e) {

                e.preventDefault();
                e.stopPropagation();

                var scope = this,
                    $lux = scope.$lux,
                    form = this[this.formName],
                    model = this[this.formModelName],
                    attrs = this.formAttrs,
                    target = attrs.action,
                    FORMKEY = scope.formAttrs.FORMKEY,
                    method = attrs.method || 'post',
                    uploadHeaders = {},
                    promise,
                    api,
                    uploadUrl,
                    deferred;
                //
                // Flag the form as submitted
                form.submitted = true;
                if (form.$invalid) return;

                // Get the api information if target is an object
                //	target
                //		- name:	api name
                //		- target: api target
                if (isObject(target)) api = $lux.api(target);

                this.formMessages = {};
                //
                if (scope.formProcessor === 'ngFileUpload') {
                    if (api) {
                        promise = api.getUrlForTarget(target).then(function (url) {
                            uploadUrl = url;
                            uploadHeaders.Authorization = 'bearer ' + api.token();
                        });
                    } else {
                        deferred = $lux.q.defer();
                        uploadUrl = target;
                        deferred.resolve();
                        promise = deferred.promise;
                    }
                    promise = promise.then(function () {
                        return Upload.upload({
                            url: uploadUrl,
                            headers: uploadHeaders,
                            data: model
                        });
                    });
                } else if (api) {
                    promise = api.request(method, target, model);
                } else if (target) {
                    var enctype = attrs.enctype || 'application/json',
                        ct = enctype.split(';')[0],
                        options = {
                            url: target,
                            method: attrs.method || 'POST',
                            data: model,
                            transformRequest: $lux.formData(ct)
                        };
                    // Let the browser choose the content type
                    if (ct === 'application/x-www-form-urlencoded' || ct === 'multipart/form-data') {
                        options.headers = {
                            'content-type': undefined
                        };
                    } else {
                        options.headers = {
                            'content-type': ct
                        };
                    }
                    promise = $lux.http(options);
                } else {
                    $lux.log.error('Could not process form. No target or api');
                    return;
                }
                //
                promise.then(
                    function (response) {
                        var data = response.data;
                        var hookName = scope.formAttrs.resultHandler;
                        var hook = hookName && $lux.formHandlers[hookName];
                        if (hook) {
                            hook(response, scope);
                        } else if (data.messages) {
                            scope.addMessages(data.messages);
                        } else if (api) {
                            // Created
                            var message = data.message;
                            if (!message) {
                                if (response.status === 201)
                                    message = 'Successfully created';
                                else
                                    message = 'Successfully updated';
                            }
                            $lux.messages.info(message);
                        }
                    },
                    function (response) {
                        var data = response.data || {};

                        if (data.errors) {
                            scope.addMessages(data.errors, 'error');
                        } else {
                            var message = data.message;
                            if (!message) {
                                var status = status || data.status || 501;
                                message = 'Response error (' + status + ')';
                            }
                            $lux.messages.error(message);
                        }
                    });
            };
        }]);

});

define('lux/forms',['angular',
        'lux',
        'lux/forms/utils',
        'lux/forms/handlers',
        'lux/forms/process'], function (angular, lux) {
    "use strict";

    var $ = angular.element,
        extend = angular.extend,
        forEach = angular.forEach,
        getOptions = lux.getOptions,
        isString = lux.isString,
        isObject = lux.isObject,
        isArray = lux.isArray,
        formid = function () {
            return 'f' + lux.s4();
        };

    lux.forms = {
        directives: {}
    };
    //
    // Form module for lux
    //
    //  Forms are created form a JSON object
    //
    //  Forms layouts:
    //
    //      - default
    //      - inline
    //      - horizontal
    //
    //  Events:
    //
    //      formReady: triggered once the form has rendered
    //          arguments: formmodel, formscope
    //
    //      formFieldChange: triggered when a form field changes:
    //          arguments: formmodel, field (changed)
    //
    angular.module('lux.form', ['lux.form.utils', 'lux.form.handlers', 'ngFileUpload', 'lux.form.process'])
        //
        .constant('formDefaults', {
            // Default layout
            layout: 'default',
            // for horizontal layout
            labelSpan: 2,
            showLabels: true,
            novalidate: true,
            //
            dateTypes: ['date', 'datetime', 'datetime-local'],
            defaultDatePlaceholder: 'YYYY-MM-DD',
            //
            formErrorClass: 'form-error',
            FORMKEY: 'm__form',
            useNgFileUpload: true
        })
        //
        .constant('defaultFormElements', function () {
            return {
                'text': {element: 'input', type: 'text', editable: true, textBased: true},
                'date': {element: 'input', type: 'date', editable: true, textBased: true},
                'datetime': {element: 'input', type: 'datetime', editable: true, textBased: true},
                'datetime-local': {element: 'input', type: 'datetime-local', editable: true, textBased: true},
                'email': {element: 'input', type: 'email', editable: true, textBased: true},
                'month': {element: 'input', type: 'month', editable: true, textBased: true},
                'number': {element: 'input', type: 'number', editable: true, textBased: true},
                'password': {element: 'input', type: 'password', editable: true, textBased: true},
                'search': {element: 'input', type: 'search', editable: true, textBased: true},
                'tel': {element: 'input', type: 'tel', editable: true, textBased: true},
                'textarea': {element: 'textarea', editable: true, textBased: true},
                'time': {element: 'input', type: 'time', editable: true, textBased: true},
                'url': {element: 'input', type: 'url', editable: true, textBased: true},
                'week': {element: 'input', type: 'week', editable: true, textBased: true},
                //  Specialized editables
                'checkbox': {element: 'input', type: 'checkbox', editable: true, textBased: false},
                'color': {element: 'input', type: 'color', editable: true, textBased: false},
                'file': {element: 'input', type: 'file', editable: true, textBased: false},
                'range': {element: 'input', type: 'range', editable: true, textBased: false},
                'select': {element: 'select', editable: true, textBased: false},
                //  Pseudo-non-editables (containers)
                'checklist': {element: 'div', editable: false, textBased: false},
                'fieldset': {element: 'fieldset', editable: false, textBased: false},
                'div': {element: 'div', editable: false, textBased: false},
                'form': {element: 'form', editable: false, textBased: false},
                'radio': {element: 'div', editable: false, textBased: false},
                //  Non-editables (mostly buttons)
                'button': {element: 'button', type: 'button', editable: false, textBased: false},
                'hidden': {element: 'input', type: 'hidden', editable: false, textBased: false},
                'image': {element: 'input', type: 'image', editable: false, textBased: false},
                'legend': {element: 'legend', editable: false, textBased: false},
                'reset': {element: 'button', type: 'reset', editable: false, textBased: false},
                'submit': {element: 'button', type: 'submit', editable: false, textBased: false}
            };
        })
        //
        .factory('formElements', ['defaultFormElements', function (defaultFormElements) {
            return defaultFormElements;
        }])
        //
        .run(['$rootScope', '$lux', function (scope, $lux) {
            //
            //  Listen for a Lux form to be available
            //  If it uses the api for posting, register with it
            scope.$on('formReady', function (e, model, formScope) {
                var attrs = formScope.formAttrs,
                    action = attrs ? attrs.action : null,
                    actionType = attrs ? attrs.actionType : null;

                if (isObject(action) && actionType !== 'create') {
                    var api = $lux.api(action);
                    if (api) {
                        $lux.log.info('Form ' + formScope.formModelName + ' registered with "' +
                            api.toString() + '" api');
                        api.formReady(model, formScope);
                    }
                }
            });
        }])

        //
        // The formService is a reusable component for redering form fields
        .service('standardForm', ['$log', '$http', '$document', '$templateCache', 'formDefaults', 'formElements',
                                  function (log, $http, $document, $templateCache, formDefaults, formElements) {
            //
            var baseAttributes = ['id', 'name', 'title', 'style'],
                inputAttributes = extendArray([], baseAttributes, ['disabled', 'readonly', 'type', 'value', 'placeholder',
                                                                  'autocapitalize', 'autocorrect']),
                textareaAttributes = extendArray([], baseAttributes, ['disabled', 'readonly', 'placeholder', 'rows', 'cols']),
                buttonAttributes = extendArray([], baseAttributes, ['disabled']),
                // Don't include action in the form attributes
                formAttributes = extendArray([], baseAttributes, ['accept-charset','autocomplete',
                                                                  'enctype', 'method', 'novalidate', 'target']),
                validationAttributes = ['minlength', 'maxlength', 'min', 'max', 'required'],
                ngAttributes = ['disabled', 'minlength', 'maxlength', 'required'],
                elements = formElements();

            extend(this, {
                name: 'default',
                //
                className: '',
                //
                inputGroupClass: 'form-group',
                //
                inputHiddenClass: 'form-hidden',
                //
                inputClass: 'form-control',
                //
                buttonClass: 'btn btn-default',
                //
                template: function (url) {
                    return $http.get(url, {cache: $templateCache}).then(function (result) {
                        return result.data;
                    });
                },
                //
                // Create a form element
                createElement: function (driver, scope) {

                    /**
                     * Builds infomation about type and text mode used in the field.
                     * These informations are used in `api.formReady` method.

                     * @param formModelName {string} - name of the model
                     * @param field {object}
                     * @param fieldType {string} - type of the field
                     */
                    function buildFieldInfo (formModelName, field, fieldType) {
                        var typeConfig = formModelName + 'Type';
                        var textMode = getJsonOrNone(field.text_edit);
                        scope[typeConfig] = scope[typeConfig] || {};

                        if (textMode !== null)
                            scope[typeConfig][field.name] = textMode.mode || '';
                        else
                            scope[typeConfig][field.name] = fieldType;
                    }

                    var self = this,
                        thisField = scope.field,
                        tc = thisField.type.split('.'),
                        info = elements[tc.splice(0, 1)[0]],
                        renderer,
                        fieldType;

                    scope.extraClasses = tc.join(' ');
                    scope.info = info;

                    if (info) {
                        if (info.hasOwnProperty('type') && typeof this[info.type] === 'function')
                            // Pick the renderer by checking `type`
                            fieldType = info.type;
                        else
                            // If no element type, use the `element`
                            fieldType = info.element;
                    }

                    renderer = this[fieldType];

                    buildFieldInfo(scope.formModelName, thisField, fieldType);

                    if (!renderer)
                        renderer = this.renderNotElements;

                    var element = renderer.call(this, scope);

                    forEach(scope.children, function (child) {
                        var field = child.field;

                        if (field) {

                            // extend child.field with options
                            forEach(formDefaults, function (_, name) {
                                if (field[name] === undefined)
                                    field[name] = scope.field[name];
                            });
                            //
                            // Make sure children is defined, otherwise it will be inherited from the parent scope
                            if (child.children === undefined)
                                child.children = null;
                            child = driver.createElement(extend(scope, child));

                            if (isArray(child))
                                forEach(child, function (c) {
                                    element.append(c);
                                });
                            else if (child)
                                element.append(child);
                        } else {
                            log.error('form child without field');
                        }
                    });
                    // Reinstate the field
                    scope.field = thisField;
                    return element;
                },
                //
                addAttrs: function (scope, element, attributes) {
                    forEach(scope.field, function (value, name) {
                        if (attributes.indexOf(name) > -1) {
                            if (ngAttributes.indexOf(name) > -1)
                                element.attr('ng-' + name, value);
                            else
                                element.attr(name, value);
                        } else if (name.substring(0, 5) === 'data-') {
                            element.attr(name, value);
                        }
                    });
                    return element;
                },
                //
                addDirectives: function(scope, element) {
                    // lux-codemirror directive
                    if (scope.field.hasOwnProperty('text_edit')) {
                        element.attr('lux-codemirror', scope.field.text_edit);
                    } else if (formDefaults.dateTypes.indexOf(scope.field.type) > -1) {
                        // Convert date string to date object
                        element.attr('format-date', '');
                    } else if (scope.formAttrs.useNgFileUpload && scope.field.type === 'file') {
                        element.attr('ngf-select', '');
                        scope.formProcessor = 'ngFileUpload';
                    }
                    return element;
                },
                //
                renderNotForm: function (scope) {
                    return $($document[0].createElement('span')).html(field.label || '');
                },
                //
                fillDefaults: function (scope) {
                    var field = scope.field;
                    field.label = field.label || field.name;
                    scope.formCount++;
                    if (!field.id)
                        field.id = field.name + '-' + scope.formid + '-' + scope.formCount;
                },
                //
                form: function (scope) {
                    var field = scope.field,
                        info = scope.info,
                        form = $($document[0].createElement(info.element))
                                    .attr('role', 'form').addClass(this.className)
                                    .attr('ng-model', field.model);
                    this.formMessages(scope, form);
                    return this.addAttrs(scope, form, formAttributes);
                },
                //
                'ng-form': function (scope) {
                    return this.form(scope);
                },
                //
                // Render a fieldset
                fieldset: function (scope) {
                    var field = scope.field,
                        info = scope.info,
                        element = $($document[0].createElement(info.element));
                    if (field.label)
                        element.append($($document[0].createElement('legend')).html(field.label));
                    return element;
                },
                //
                div: function (scope) {
                    var info = scope.info,
                        element = $($document[0].createElement(info.element)).addClass(scope.extraClasses);
                    return element;
                },
                //
                radio: function (scope) {
                    this.fillDefaults(scope);

                    var field = scope.field,
                        info = scope.info,
                        input = angular.element($document[0].createElement(info.element)),
                        label = angular.element($document[0].createElement('label')).attr('for', field.id),
                        span = angular.element($document[0].createElement('span'))
                                    .css('margin-left', '5px')
                                    .css('position', 'relative')
                                    .css('bottom', '2px')
                                    .html(field.label),
                        element = angular.element($document[0].createElement('div')).addClass(this.element);

                    input.attr('ng-model', scope.formModelName + '["' + field.name + '"]');

                    forEach(inputAttributes, function (name) {
                        if (field[name]) input.attr(name, field[name]);
                    });

                    label.append(input).append(span);
                    element.append(label);
                    return this.onChange(scope, this.inputError(scope, element));
                },
                //
                checkbox: function (scope) {
                    return this.radio(scope);
                },
                //
                input: function (scope, attributes) {
                    this.fillDefaults(scope);

                    var field = scope.field,
                        info = scope.info,
                        input = angular.element($document[0].createElement(info.element)).addClass(this.inputClass),
                        label = angular.element($document[0].createElement('label')).attr('for', field.id).html(field.label),
                        element;

                    // Add model attribute
                    input.attr('ng-model', scope.formModelName + '["' + field.name + '"]');

                    // Add default placeholder to date field if not exist
                    if (field.type === 'date' && field.placeholder === undefined) {
                        field.placeholder = formDefaults.defaultDatePlaceholder;
                    }

                    if (!field.showLabels || field.type === 'hidden') {
                        label.addClass('sr-only');
                        // Add placeholder if not defined
                        if (field.placeholder === undefined)
                            field.placeholder = field.label;
                    }

                    this.addAttrs(scope, input, attributes || inputAttributes);
                    if (field.value !== undefined) {
                        scope[scope.formModelName][field.name] = field.value;
                        if (info.textBased)
                            input.attr('value', field.value);
                    }

                    // Add directive to element
                    input = this.addDirectives(scope, input);

                    if (this.inputGroupClass) {
                        element = angular.element($document[0].createElement('div'));
                        if (field.type === 'hidden') element.addClass(this.inputHiddenClass);
                        else element.addClass(this.inputGroupClass);
                        element.append(label).append(input);
                    } else {
                        element = [label, input];
                    }
                    return this.onChange(scope, this.inputError(scope, element));
                },
                //
                textarea: function (scope) {
                    return this.input(scope, textareaAttributes);
                },
                //
                // Create a select element
                select: function (scope) {
                    var field = scope.field,
                        groups = {},
                        groupList = [],
                        options = [],
                        group;

                    forEach(field.options, function (opt) {
                        if (typeof(opt) === 'string') {
                            opt = {'value': opt};
                        } else if (isArray(opt)) {
                            opt = {'value': opt[0], 'repr': opt[1] || opt[0]};
                        }
                        if (opt.group) {
                            group = groups[opt.group];
                            if (!group) {
                                group = {name: opt.group, options: []};
                                groups[opt.group] = group;
                                groupList.push(group);
                            }
                            group.options.push(opt);
                        } else
                            options.push(opt);
                        // Set the default value if not available
                        if (!field.value) field.value = opt.value;
                    });

                    var info = scope.info,
                        element = this.input(scope);

                    if (elements.select.hasOwnProperty('widget') && elements.select.widget.name === 'selectUI')
                        // UI-Select widget
                        this.selectUI(scope, element, field, groupList, options);
                    else
                        // Standard select
                        this.selectStandard(scope, element, field, groupList, options);

                    return this.onChange(scope, element);
                },
                //
                // Standard select widget
                selectStandard: function(scope, element, field, groupList, options) {
                    var groups = {},
                        group, grp,
                        select = this._select(scope.info.element, element);

                    if (groupList.length) {
                        if (options.length)
                            groupList.push({name: 'other', options: options});

                        forEach(groupList, function (group) {
                            grp = $($document[0].createElement('optgroup'))
                                    .attr('label', group.name);
                            select.append(grp);
                            forEach(group.options, function (opt) {
                                opt = $($document[0].createElement('option'))
                                        .attr('value', opt.value).html(opt.repr || opt.value);
                                grp.append(opt);
                            });
                        });
                    } else {
                        forEach(options, function (opt) {
                            opt = $($document[0].createElement('option'))
                                    .attr('value', opt.value).html(opt.repr || opt.value);
                            select.append(opt);
                        });
                    }

                    if (field.multiple)
                        select.attr('multiple', true);
                },
                //
                // UI-Select widget
                selectUI: function(scope, element, field, groupList, options) {
                    //
                    scope.groupBy = function (item) {
                        return item.group;
                    };
                    // Search specified global
                    scope.enableSearch = elements.select.widget.enableSearch;

                    // Search specified for field
                    if (field.hasOwnProperty('search'))
                        scope.enableSearch = field.search;

                    var selectUI = $($document[0].createElement('ui-select'))
                                    .attr('id', field.id)
                                    .attr('name', field.name)
                                    .attr('ng-model', scope.formModelName + '["' + field.name + '"]')
                                    .attr('theme', elements.select.widget.theme)
                                    .attr('search-enabled', 'enableSearch')
                                    .attr('ng-change', 'fireFieldChange("' + field.name + '")'),
                        match = $($document[0].createElement('ui-select-match'))
                                    .attr('placeholder', 'Select or search ' + field.label.toLowerCase()),
                        choices_inner = $($document[0].createElement('div')),
                        choices_inner_small = $($document[0].createElement('small')),
                        choices = $($document[0].createElement('ui-select-choices'))
                                    // Ensure any inserted placeholders are disabled
                                    // i.e. 'Please Select...'
                                    .attr('ui-disable-choice', 'item.id === "placeholder"')
                                    .append(choices_inner);

                    if (field.multiple)
                        selectUI.attr('multiple', true);

                    if (field.hasOwnProperty('data-remote-options')) {
                        // Remote options
                        selectUI.attr('data-remote-options', field['data-remote-options'])
                                .attr('data-remote-options-id', field['data-remote-options-id'])
                                .attr('data-remote-options-value', field['data-remote-options-value'])
                                .attr('data-remote-options-params', field['data-remote-options-params']);

                        if (field.multiple)
                            match.html('{{$item.repr || $item.name || $item.id}}');
                        else
                            match.html('{{$select.selected.name || $select.selected.id}}');

                        choices.attr('repeat', field['data-ng-options-ui-select'] + ' | filter: $select.search');
                        choices_inner.html('{{item.name || item.id}}');
                    } else {
                        // Local options
                        var optsId = field.name + '_opts',
                            repeatItems = 'opt.value as opt in ' + optsId + ' | filter: $select.search';

                        if (field.multiple)
                            match.html('{{$item.value}}');
                        else
                            match.html('{{$select.selected.value}}');

                        if (groupList.length) {
                            // Groups require raw options
                            scope[optsId] = field.options;
                            choices.attr('group-by', 'groupBy')
                                   .attr('repeat', repeatItems);
                            choices_inner.attr('ng-bind-html', 'opt.repr || opt.value');
                        } else {
                            scope[optsId] = options;
                            choices.attr('repeat', repeatItems);

                            if (options.length > 0) {
                                var attrsNumber = Object.keys(options[0]).length;
                                choices_inner.attr('ng-bind-html', 'opt.repr || opt.value');

                                if (attrsNumber > 1) {
                                    choices_inner_small.attr('ng-bind-html', 'opt.value');
                                    choices.append(choices_inner_small);
                                }
                            }
                        }
                    }

                    selectUI.append(match);
                    selectUI.append(choices);
                    element[0].replaceChild(selectUI[0], element[0].childNodes[1]);
                },
                //
                button: function (scope) {
                    var field = scope.field,
                        info = scope.info,
                        element = $($document[0].createElement(info.element)).addClass(this.buttonClass);
                    field.name = field.name || info.element;
                    field.label = field.label || field.name;
                    element.html(field.label);
                    this.addAttrs(scope, element, buttonAttributes);
                    return this.onClick(scope, element);
                },
                //
                onClick: function (scope, element) {
                    var name = element.attr('name'),
                        field = scope.field,
                        clickname = name + 'Click',
                        self = this;
                    //
                    // scope function
                    scope[clickname] = function (e) {
                        if (scope.$broadcast(clickname, e).defaultPrevented) return;
                        if (scope.$emit(clickname, e).defaultPrevented) return;

                        // Get the form processing function
                        var callback = self.processForm(scope);
                        //
                        if (field.click) {
                            callback = getRootAttribute(field.click);
                            if (!angular.isFunction(callback)) {
                                log.error('Could not locate click function "' + field.click + '" for button');
                                return;
                            }
                        }
                        callback.call(this, e);
                    };
                    element.attr('ng-click', clickname + '($event)');
                    return element;
                },
                //
                //  Add change event
                onChange: function (scope, element) {
                    var field = scope.field,
                        input = $(element[0].querySelector(scope.info.element));
                    input.attr('ng-change', 'fireFieldChange("' + field.name + '")');
                    return element;
                },
                //
                // Add input error elements to the input element.
                // Each input element may have one or more error handler depending
                // on its type and attributes
                inputError: function (scope, element) {
                    var field = scope.field,
                        self = this,
                        // True when the form is submitted
                        submitted = scope.formName + '.submitted',
                        // True if the field is dirty
                        dirty = joinField(scope.formName, field.name, '$dirty'),
                        invalid = joinField(scope.formName, field.name, '$invalid'),
                        error = joinField(scope.formName, field.name, '$error') + '.',
                        input = $(element[0].querySelector(scope.info.element)),
                        p = $($document[0].createElement('p'))
                                .attr('ng-show', '(' + submitted + ' || ' + dirty + ') && ' + invalid)
                                .addClass('text-danger error-block')
                                .addClass(scope.formErrorClass),
                        value,
                        attrname;
                    // Loop through validation attributes
                    forEach(validationAttributes, function (attr) {
                        value = field[attr];
                        attrname = attr;
                        if (value !== undefined && value !== false && value !== null) {
                            if (ngAttributes.indexOf(attr) > -1) attrname = 'ng-' + attr;
                            input.attr(attrname, value);
                            p.append($($document[0].createElement('span'))
                                         .attr('ng-show', error + attr)
                                         .html(self.errorMessage(scope, attr)));
                        }
                    });

                    // Add the invalid handler if not available
                    var errors = p.children().length,
                        nameError = '$invalid';
                    if (errors)
                        nameError += ' && !' + joinField(scope.formName, field.name, '$error.required');
                        // Show only if server side errors don't exist
                        nameError += ' && !formErrors.' + field.name;
                    p.append(this.fieldErrorElement(scope, nameError, self.errorMessage(scope, 'invalid')));

                    // Add the invalid handler for server side errors
                    var name = '$invalid';
                        name += ' && !' + joinField(scope.formName, field.name, '$error.required');
                        // Show only if server side errors exists
                        name += ' && formErrors.' + field.name;
                    p.append(
                        this.fieldErrorElement(scope, name, self.errorMessage(scope, 'invalid'))
                        .html('{{formErrors["' + field.name + '"]}}')
                    );

                    return element.append(p);
                },
                //
                fieldErrorElement: function (scope, name, msg) {
                    var field = scope.field,
                        value = joinField(scope.formName, field.name, name);

                    return $($document[0].createElement('span'))
                                .attr('ng-show', value)
                                .html(msg);
                },
                //
                // Add element which containes form messages and errors
                formMessages: function (scope, form) {
                    var messages = $($document[0].createElement('p')),
                        a = scope.formAttrs;
                    messages.attr('ng-repeat', 'message in formMessages.' + a.FORMKEY)
                            .attr('ng-bind', 'message.message')
                            .attr('ng-class', "message.error ? 'text-danger' : 'text-info'");
                    return form.append(messages);
                },
                //
                errorMessage: function (scope, attr) {
                    var message = attr + 'Message',
                        field = scope.field,
                        handler = this[attr+'ErrorMessage'] || this.defaultErrorMesage;
                    return field[message] || handler.call(this, scope);
                },
                //
                // Default error Message when the field is invalid
                defaultErrorMesage: function (scope) {
                    var type = scope.field.type;
                    return 'Not a valid ' + type;
                },
                //
                minErrorMessage: function (scope) {
                    return 'Must be greater than ' + scope.field.min;
                },
                //
                maxErrorMessage: function (scope) {
                    return 'Must be less than ' + scope.field.max;
                },
                //
                maxlengthErrorMessage: function (scope) {
                    return 'Too long, must be less than ' + scope.field.maxlength;
                },
                //
                minlengthErrorMessage: function (scope) {
                    return 'Too short, must be more than ' + scope.field.minlength;
                },
                //
                requiredErrorMessage: function (scope) {
                    var msg = scope.field.required_error;
                    return msg || scope.field.label + " is required";
                },
                //
                // Return the function to handle form processing
                processForm: function (scope) {
                    return scope.processForm || lux.processForm;
                },
                //
                _select: function (tag, element) {
                    if (isArray(element)) {
                        for (var i=0; i<element.length; ++i) {
                            if (element[0].tagName === tag)
                                return element;
                        }
                    } else {
                        return $(element[0].querySelector(tag));
                    }
                }
            });
        }])
        //
        // Bootstrap Horizontal form renderer
        .service('horizontalForm', ['$document', 'standardForm',
                                    function ($document, standardForm) {
            //
            // extend the standardForm service
            extend(this, standardForm, {

                name: 'horizontal',

                className: 'form-horizontal',

                input: function (scope) {
                    var element = standardForm.input(scope),
                        children = element.children(),
                        labelSpan = scope.field.labelSpan ? +scope.field.labelSpan : 2,
                        wrapper = $($document[0].createElement('div'));
                    labelSpan = Math.max(2, Math.min(labelSpan, 10));
                    $(children[0]).addClass('control-label col-sm-' + labelSpan);
                    wrapper.addClass('col-sm-' + (12-labelSpan));
                    for (var i=1; i<children.length; ++i)
                        wrapper.append($(children[i]));
                    return element.append(wrapper);
                },

                button: function (scope) {
                    var element = standardForm.button(scope),
                        labelSpan = scope.field.labelSpan ? +scope.field.labelSpan : 2,
                        outer = $($document[0].createElement('div')).addClass(this.inputGroupClass),
                        wrapper = $($document[0].createElement('div'));
                    labelSpan = Math.max(2, Math.min(labelSpan, 10));
                    wrapper.addClass('col-sm-offset-' + labelSpan)
                           .addClass('col-sm-' + (12-labelSpan));
                    outer.append(wrapper.append(element));
                    return outer;
                }
            });
        }])
        //
        .service('inlineForm', ['standardForm', function (standardForm) {
            extend(this, standardForm, {

                name: 'inline',

                className: 'form-inline',

                input: function (scope) {
                    var element = standardForm.input(scope);
                    $(element[0].getElementsByTagName('label')).addClass('sr-only');
                    return element;
                }
            });
        }])
        //
        .service('formBaseRenderer', ['$lux', '$compile', 'formDefaults',
                function ($lux, $compile, formDefaults) {
            //
            // Internal function for compiling a scope
            this.createElement = function (scope) {
                var field = scope.field;

                if (this[field.layout])
                    return this[field.layout].createElement(this, scope);
                else
                    $lux.log.error('Layout "' + field.layout + '" not available, cannot render form');
            };
            //
            // Initialise the form scope
            this.initScope = function (scope, element, attrs) {
                var data = getOptions(attrs);

                // No data, maybe this form was loaded via angular ui router
                // try to evaluate internal scripts
                if (!data) {
                    var scripts= element[0].getElementsByTagName('script');
                    forEach(scripts, function (js) {
                        globalEval(js.innerHTML);
                    });
                    data = getOptions(attrs);
                }

                if (data && data.field) {
                    var form = data.field,
                        formmodel = {};

                    // extend with form defaults
                    data.field = extend({}, formDefaults, form);
                    extend(scope, data);
                    form = scope.field;
                    if (form.model) {
                        if (!form.name)
                            form.name = form.model + 'form';
                        scope.$parent[form.model] = formmodel;
                    } else {
                        if (!form.name)
                            form.name = 'form';
                        form.model = form.name + 'Model';
                    }
                    scope.formName = form.name;
                    scope.formModelName = form.model;
                    //
                    scope[scope.formModelName] = formmodel;
                    scope.formAttrs = form;
                    scope.formClasses = {};
                    scope.formErrors = {};
                    scope.formMessages = {};
                    scope.$lux = $lux;
                    if (!form.id)
                        form.id = 'f' + s4();
                    scope.formid = form.id;
                    scope.formCount = 0;

                    scope.addMessages = function (messages, error) {

                        forEach(messages, function (message) {
                            if (isString(message))
                                message = {message: message};

                            var field = message.field;
                            if (field && !scope[scope.formName].hasOwnProperty(field)) {
                                message.message = field + ' ' + message.message;
                                field = formDefaults.FORMKEY;
                            } else if (!field) {
                                field = formDefaults.FORMKEY;
                            }

                            if (error) message.error = error;

                            scope.formMessages[field] = [message];

                            if (message.error && field !== formDefaults.FORMKEY) {
                                scope.formErrors[field] = message.message;
                                scope[scope.formName][field].$invalid = true;
                            }
                        });
                    };

                    scope.fireFieldChange = function (field) {
                        // Delete previous field error from server side
                        if (scope.formErrors[field] !== undefined) {
                            delete scope.formErrors[field];
                        }
                        // Triggered every time a form field changes
                        scope.$broadcast('fieldChange', formmodel, field);
                        scope.$emit('formFieldChange', formmodel, field);
                    };
                } else {
                    $lux.log.error('Form data does not contain field entry');
                }
            };
            //
            this.createForm = function (scope, element) {
                var form = scope.field;
                if (form) {
                    var formElement = this.createElement(scope);
                    //  Compile and update DOM
                    if (formElement) {
                        this.preCompile(scope, formElement);
                        $compile(formElement)(scope);
                        element.replaceWith(formElement);
                        this.postCompile(scope, formElement);
                    }
                }
            };

            this.preCompile = function () {};

            this.postCompile = function () {};

            this.checkField = function (name) {
                var checker = this['check_' + name];
                // There may be a custom field checker
                if (checker)
                    checker.call(this);
                else {
                    var field = this.form[name];
                    if (field.$valid)
                        this.formClasses[name] = 'has-success';
                    else if (field.$dirty) {
                        this.formErrors[name] = name + ' is not valid';
                        this.formClasses[name] = 'has-error';
                    }
                }
            };

            this.processForm = function(scope) {
                // Clear form errors and messages
                scope.formMessages = [];
                scope.formErrors = [];

                if (scope.form.$invalid) {
                    return $scope.showErrors();
                }
            };
        }])
        //
        // Default form Renderer, roll your own if you like
        .service('formRenderer', ['formBaseRenderer', 'standardForm', 'horizontalForm', 'inlineForm',
            function (base, stdForm, horForm, inlForm) {
                var renderer = extend(this, base);
                this[stdForm.name] = stdForm;
                this[horForm.name] = horForm;
                this[inlForm.name] = inlForm;

                // Create the directive
                this.directive = function () {

                    return {
                        restrict: "AE",
                        //
                        scope: {},
                        //
                        compile: function () {
                            return {
                                pre: function (scope, element, attr) {
                                    // Initialise the scope from the attributes
                                    renderer.initScope(scope, element, attr);
                                },
                                post: function (scope, element) {
                                    // create the form
                                    renderer.createForm(scope, element);
                                    // Emit the form upwards through the scope hierarchy
                                    scope.$emit('formReady', scope[scope.formModelName], scope);
                                }
                            };
                        }
                    };
                };
            }
        ])
        //
        // Lux form
        .directive('luxForm', ['formRenderer', function (formRenderer) {
            return formRenderer.directive();
        }])
        //
        .directive("checkRepeat", ['$log', function (log) {
            return {
                require: "ngModel",

                restrict: 'A',

                link: function(scope, element, attrs, ctrl) {
                    var other = element.inheritedData("$formController")[attrs.checkRepeat];
                    if (other) {
                        ctrl.$parsers.push(function(value) {
                            if(value === other.$viewValue) {
                                ctrl.$setValidity("repeat", true);
                                return value;
                            }
                            ctrl.$setValidity("repeat", false);
                        });

                        other.$parsers.push(function(value) {
                            ctrl.$setValidity("repeat", value === ctrl.$viewValue);
                            return value;
                        });
                    } else {
                        log.error('Check repeat directive could not find ' + attrs.checkRepeat);
                    }
                 }
            };
        }])
        //
        // A directive which add keyup and change event callaback
        .directive('watchChange', function() {
            return {
                scope: {
                    onchange: '&watchChange'
                },
                //
                link: function(scope, element, attrs) {
                    element.on('keyup', function() {
                        scope.$apply(function () {
                            scope.onchange();
                        });
                    }).on('change', function() {
                        scope.$apply(function () {
                            scope.onchange();
                        });
                    });
                }
            };
        })
        //
        // Format string date to date object
        .directive('formatDate', function () {
            return {
                require: '?ngModel',
                link: function (scope, elem, attrs, ngModel) {
                    // All date-related inputs like <input type="date">
                    // require the model to be a Date object in Angular 1.3+.
                    ngModel.$formatters.push(function(modelValue){
                        if (typeof modelValue === 'string' || typeof modelValue === 'number')
                            return new Date(modelValue);
                        return modelValue;
                    });
                }
            };
        });

    return lux.forms;

    function joinField(model, name, extra) {
        return model + '["' + name + '"].' + extra;
    }
});

require([
    'require.config',
    'angular',
    'giotto',
    'lux/forms'
], function(lux, angular, d3) {

    lux.bootstrap('luxsite', []);
});

define("app", function(){});

