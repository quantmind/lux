/* eslint-plugin-disable angular */
define('lux/config/lux',[],function () {
    'use strict';

    var root = window,
        lux = root.lux || {},
        ostring = Object.prototype.toString;

    if (isString(lux))
        lux = {context: urlBase64DecodeToJSON(lux)};
    else if (lux.root)
        return lux;

    root.lux = lux;

    lux.root = root;
    lux.require = extend(lux.require);
    lux.extend = extend;
    lux.isString = isString;
    lux.isArray = isArray;
    lux.isObject = isObject;
    lux.urlBase64Decode = urlBase64Decode;
    lux.urlBase64DecodeToJSON = urlBase64DecodeToJSON;

    return lux;

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

define('lux/config/paths',[],function () {
    'use strict';

    return function () {
        return {
            'angular': '//ajax.googleapis.com/ajax/libs/angularjs/1.5.5/angular',
            'angular-animate': '//ajax.googleapis.com/ajax/libs/angularjs/1.5.5/angular-animate',
            'angular-mocks': '//ajax.googleapis.com/ajax/libs/angularjs/1.5.5/angular-mocks.js',
            'angular-sanitize': '//ajax.googleapis.com/ajax/libs/angularjs/1.5.5/angular-sanitize',
            'angular-touch': '//cdnjs.cloudflare.com/ajax/libs/angular.js/1.5.5/angular-touch',
            'angular-ui-bootstrap': 'https://cdnjs.cloudflare.com/ajax/libs/angular-ui-bootstrap/1.3.2/ui-bootstrap-tpls',
            'angular-ui-router': '//cdnjs.cloudflare.com/ajax/libs/angular-ui-router/0.2.14/angular-ui-router',
            'angular-ui-select': '//cdnjs.cloudflare.com/ajax/libs/angular-ui-select/0.14.9/select',
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
            'd3': '//cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3',
            'google-analytics': '//www.google-analytics.com/analytics.js',
            'gridster': '//cdnjs.cloudflare.com/ajax/libs/jquery.gridster/0.5.6/jquery.gridster',
            'holder': '//cdnjs.cloudflare.com/ajax/libs/holder/2.3.1/holder',
            'highlight': '//cdnjs.cloudflare.com/ajax/libs/highlight.js/9.1.0/highlight.min.js',
            'katex': '//cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js',
            'katex-css': '//cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css',
            'leaflet': '//cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/leaflet.js',
            'lodash': '//cdnjs.cloudflare.com/ajax/libs/lodash.js/3.10.1/lodash',
            'marked': '//cdnjs.cloudflare.com/ajax/libs/marked/0.3.2/marked',
            'mathjax': '//cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML',
            'moment': '//cdnjs.cloudflare.com/ajax/libs/moment.js/2.10.6/moment',
            'restangular': '//cdnjs.cloudflare.com/ajax/libs/restangular/1.4.0/restangular',
            'sockjs': '//cdnjs.cloudflare.com/ajax/libs/sockjs-client/1.0.3/sockjs',
            'stats': '//cdnjs.cloudflare.com/ajax/libs/stats.js/r11/Stats',
            'topojson': '//cdnjs.cloudflare.com/ajax/libs/topojson/1.6.19/topojson'
        };
    };

});

define('lux/config/shim',[],function () {
    'use strict';
    // Default shim
    return function (root) {
        return {
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
    };

});

/* eslint-plugin-disable angular */
define('lux/config/main',['lux/config/lux',
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


/* eslint-plugin-disable angular */
define('require.config',['lux/config/main'], function (lux) {
    'use strict';

    var localRequiredPath = lux.PATH_TO_LOCAL_REQUIRED_FILES || '';

    lux.require.paths = lux.extend(lux.require.paths, {
        'angular-img-crop': localRequiredPath + 'luxsite/ng-img-crop.js',
        'videojs': '//vjs.zencdn.net/4.12/video.js'
    });

    lux.config();

    return lux;
});

(function (exports) {
	'use strict';

	$lux.$inject = ["$controllerProvider", "$provide", "$compileProvider", "$filterProvider", "$locationProvider", "$injector"];
	luxMessage.$inject = ["$rootScope", "$log"];
	luxAce.$inject = ["$lux"];
	luxCrumbs.$inject = ["$location"];
	luxFullpage.$inject = ["$window"];
	luxForm.$inject = ["$lux", "$log", "luxFormConfig"];
	luxField.$inject = ["$log", "$lux", "luxFormConfig"];
	luxRemote.$inject = ["$lux"];
	runForm.$inject = ["$window", "luxFormConfig"];
	link.$inject = ["$location"];
	navbar.$inject = ["luxNavBarDefaults"];
	sidebar.$inject = ["luxSidebarDefaults"];
	link$1.$inject = ["luxLinkTemplate", "luxLink"];
	navbar$1.$inject = ["$window", "luxNavbarTemplate", "luxNavbar"];
	sidebar$1.$inject = ["$window", "$compile", "$timeout", "luxSidebarTemplate", "luxSidebar"];
	menuConfig.$inject = ["$luxProvider"];
	luxGrid.$inject = ["$luxProvider"];
	registerProviders.$inject = ["$luxProvider"];
	var babelHelpers = {};
	babelHelpers.typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) {
	  return typeof obj;
	} : function (obj) {
	  return obj && typeof Symbol === "function" && obj.constructor === Symbol ? "symbol" : typeof obj;
	};

	babelHelpers.classCallCheck = function (instance, Constructor) {
	  if (!(instance instanceof Constructor)) {
	    throw new TypeError("Cannot call a class as a function");
	  }
	};

	babelHelpers.createClass = function () {
	  function defineProperties(target, props) {
	    for (var i = 0; i < props.length; i++) {
	      var descriptor = props[i];
	      descriptor.enumerable = descriptor.enumerable || false;
	      descriptor.configurable = true;
	      if ("value" in descriptor) descriptor.writable = true;
	      Object.defineProperty(target, descriptor.key, descriptor);
	    }
	  }

	  return function (Constructor, protoProps, staticProps) {
	    if (protoProps) defineProperties(Constructor.prototype, protoProps);
	    if (staticProps) defineProperties(Constructor, staticProps);
	    return Constructor;
	  };
	}();

	babelHelpers.get = function get(object, property, receiver) {
	  if (object === null) object = Function.prototype;
	  var desc = Object.getOwnPropertyDescriptor(object, property);

	  if (desc === undefined) {
	    var parent = Object.getPrototypeOf(object);

	    if (parent === null) {
	      return undefined;
	    } else {
	      return get(parent, property, receiver);
	    }
	  } else if ("value" in desc) {
	    return desc.value;
	  } else {
	    var getter = desc.get;

	    if (getter === undefined) {
	      return undefined;
	    }

	    return getter.call(receiver);
	  }
	};

	babelHelpers.inherits = function (subClass, superClass) {
	  if (typeof superClass !== "function" && superClass !== null) {
	    throw new TypeError("Super expression must either be null or a function, not " + typeof superClass);
	  }

	  subClass.prototype = Object.create(superClass && superClass.prototype, {
	    constructor: {
	      value: subClass,
	      enumerable: false,
	      writable: true,
	      configurable: true
	    }
	  });
	  if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass;
	};

	babelHelpers.possibleConstructorReturn = function (self, call) {
	  if (!self) {
	    throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
	  }

	  return call && (typeof call === "object" || typeof call === "function") ? call : self;
	};

	babelHelpers;

	// some versions of angular don't export the angular module properly,
	// so we get it from window in this case.
	var angular = require('angular');
	if (!angular.version) angular = window.angular;
	var _ = angular;

	var prefix = "$";

	function Map() {}

	Map.prototype = map.prototype = {
	  constructor: Map,
	  has: function has(key) {
	    return prefix + key in this;
	  },
	  get: function get(key) {
	    return this[prefix + key];
	  },
	  set: function set(key, value) {
	    this[prefix + key] = value;
	    return this;
	  },
	  remove: function remove(key) {
	    var property = prefix + key;
	    return property in this && delete this[property];
	  },
	  clear: function clear() {
	    for (var property in this) {
	      if (property[0] === prefix) delete this[property];
	    }
	  },
	  keys: function keys() {
	    var keys = [];
	    for (var property in this) {
	      if (property[0] === prefix) keys.push(property.slice(1));
	    }return keys;
	  },
	  values: function values() {
	    var values = [];
	    for (var property in this) {
	      if (property[0] === prefix) values.push(this[property]);
	    }return values;
	  },
	  entries: function entries() {
	    var entries = [];
	    for (var property in this) {
	      if (property[0] === prefix) entries.push({ key: property.slice(1), value: this[property] });
	    }return entries;
	  },
	  size: function size() {
	    var size = 0;
	    for (var property in this) {
	      if (property[0] === prefix) ++size;
	    }return size;
	  },
	  empty: function empty() {
	    for (var property in this) {
	      if (property[0] === prefix) return false;
	    }return true;
	  },
	  each: function each(f) {
	    for (var property in this) {
	      if (property[0] === prefix) f(this[property], property.slice(1), this);
	    }
	  }
	};

	function map(object, f) {
	  var map = new Map();

	  // Copy constructor.
	  if (object instanceof Map) object.each(function (value, key) {
	    map.set(key, value);
	  });

	  // Index array by numeric index or specified key function.
	  else if (Array.isArray(object)) {
	      var i = -1,
	          n = object.length,
	          o;

	      if (f == null) while (++i < n) {
	        map.set(i, object[i]);
	      } else while (++i < n) {
	        map.set(f(o = object[i], i, object), o);
	      }
	    }

	    // Convert object to map.
	    else if (object) for (var key in object) {
	        map.set(key, object[key]);
	      }return map;
	}

	var proto = map.prototype;

	function noop() {}

	var jsLibs = {};

	function getOptions(root, attrs, optionName) {
	    var exclude = [name, 'class', 'style'],
	        options;

	    if (attrs) {
	        if (optionName) options = attrs[optionName];
	        if (!options) {
	            optionName = 'options';
	            options = attrs[optionName];
	        }
	        if (_.isString(options)) options = getAttribute(root, options);

	        if (_.isFunction(options)) options = options();
	    }
	    if (!options) options = {};

	    if (_.isObject(options)) _.forEach(attrs, function (value, name) {
	        if (name.substring(0, 1) !== '$' && exclude.indexOf(name) === -1) options[name] = value;
	    });

	    return options;
	}

	function getAttribute(obj, name) {
	    var bits = name.split('.');

	    for (var i = 0; i < bits.length; ++i) {
	        obj = obj[bits[i]];
	        if (!obj) break;
	    }
	    if (typeof obj === 'function') obj = obj();

	    return obj;
	}

	function urlBase64Decode(str) {
	    var output = str.replace('-', '+').replace('_', '/');
	    switch (output.length % 4) {
	        case 0:
	            {
	                break;
	            }
	        case 2:
	            {
	                output += '==';break;
	            }
	        case 3:
	            {
	                output += '=';break;
	            }
	        default:
	            {
	                throw 'Illegal base64url string!';
	            }
	    }
	    //polifyll https://github.com/davidchambers/Base64.js
	    return decodeURIComponent(escape(window.atob(output)));
	}

	function urlBase64DecodeToJSON(str) {
	    var decoded = urlBase64Decode(str);
	    if (!decoded) {
	        throw new Error('Cannot decode the token');
	    }
	    return JSON.parse(decoded);
	}

	function decodeJWToken(token) {
	    var parts = token.split('.');

	    if (parts.length !== 3) {
	        throw new Error('JWT must have 3 parts');
	    }

	    return urlBase64DecodeToJSON(parts[1]);
	}

	function jsLib(name, callback) {
	    var lib = jsLibs[name];

	    if (callback) {
	        if (lib) callback(lib);else {
	            require([name], function (lib) {
	                jsLibs[name] = lib || true;
	                callback(lib);
	            });
	        }
	    }

	    return lib;
	}

	function LuxException(value, message) {
	    this.value = value;
	    this.message = message;

	    this.toString = function () {
	        return this.message + ' : ' + this.value;
	    };
	}

	var isAbsolute = new RegExp('^([a-z]+://|//)');
	var DEFAULT_PORTS = { 80: 'http', 443: 'https', 21: 'ftp' };

	var urlParsingNode = void 0;
	var originUrl = void 0;

	function urlResolve(url) {

	    if (!urlParsingNode) urlParsingNode = window.document.createElement("a");

	    urlParsingNode.setAttribute('href', url);

	    // urlParsingNode provides the UrlUtils interface - http://url.spec.whatwg.org/#urlutils
	    url = {
	        href: urlParsingNode.href,
	        protocol: urlParsingNode.protocol ? urlParsingNode.protocol.replace(/:$/, '') : '',
	        host: urlParsingNode.host,
	        search: urlParsingNode.search ? urlParsingNode.search.replace(/^\?/, '') : '',
	        hash: urlParsingNode.hash ? urlParsingNode.hash.replace(/^#/, '') : '',
	        hostname: urlParsingNode.hostname,
	        port: urlParsingNode.port,
	        pathname: urlParsingNode.pathname.charAt(0) === '/' ? urlParsingNode.pathname : '/' + urlParsingNode.pathname,
	        //
	        $base: function $base() {
	            var base = url.protocol + '://' + url.hostname;
	            if (url.protocol !== DEFAULT_PORTS[+url.port]) base += ':' + url.port;
	            return base;
	        }
	    };

	    return url;
	}

	function urlIsSameOrigin(requestUrl) {
	    if (!originUrl) originUrl = urlResolve(window.location.href);
	    var parsed = _.isString(requestUrl) ? urlResolve(requestUrl) : requestUrl;
	    return parsed.protocol === originUrl.protocol && parsed.host === originUrl.host;
	}

	function urlIsAbsolute(url) {
	    return _.isString(url) && isAbsolute.test(url);
	}

	function urlJoin() {
	    var bit,
	        url = '';
	    for (var i = 0; i < arguments.length; ++i) {
	        bit = arguments[i];
	        if (bit) {
	            var cbit = bit,
	                slash = false;
	            // remove front slashes if cbit has some
	            while (url && cbit.substring(0, 1) === '/') {
	                cbit = cbit.substring(1);
	            } // remove end slashes
	            while (cbit.substring(cbit.length - 1) === '/') {
	                slash = true;
	                cbit = cbit.substring(0, cbit.length - 1);
	            }
	            if (cbit || slash) {
	                if (url && url.substring(url.length - 1) !== '/') url += '/';
	                url += cbit;
	                if (slash) url += '/';
	            }
	        }
	    }
	    return url;
	}

	var Paginator = function () {
	    function Paginator(api) {
	        babelHelpers.classCallCheck(this, Paginator);

	        this.api = api;
	    }

	    babelHelpers.createClass(Paginator, [{
	        key: 'getData',
	        value: function getData(opts, callback) {
	            if (arguments.length === 1 && _.isFunction(opts)) {
	                callback = opts;
	                opts = null;
	            }
	            this.api.get(opts).then(function (response) {
	                var data = response.data;
	                if (callback) callback(data.result);
	            });
	        }
	    }]);
	    return Paginator;
	}();

	function paginator(api) {
	    return new Paginator(api);
	}

	paginator.prototype = Paginator.prototype;

	var ENCODE_URL_METHODS = ['delete', 'get', 'head', 'options'];
	//  HTTP verbs which don't send a csrf token in their requests
	var NO_CSRF = ['get', 'head', 'options'];
	//
	var luxId = 0;

	function windowContext($window) {
	    var doc = $window.document,
	        context = $window.lux,
	        name = _.element(doc.querySelector('meta[name=csrf-param]')).attr('content'),
	        token = _.element(doc.querySelector('meta[name=csrf-token]')).attr('content'),
	        user = _.element(doc.querySelector('meta[name=user-token]')).attr('content');

	    if (_.isString(context)) context = decodeJWToken(context);
	    if (!_.isObject(context)) context = {};

	    if (name && token) {
	        context.csrf = {};
	        context.csrf[name] = token;
	    }
	    if (user) {
	        context.userToken = user;
	        context.user = decodeJWToken(user);
	    }
	    return context;
	}

	var Lux = function () {
	    function Lux(core, plugins) {
	        babelHelpers.classCallCheck(this, Lux);

	        _.extend(this, core, plugins);
	        this.$apis = map();
	    }

	    // Return the csrf key-value token to post in forms


	    babelHelpers.createClass(Lux, [{
	        key: 'api',
	        value: function api(action, ApiClass) {
	            if (arguments.length === 2) {
	                if (!_.isString(action)) throw new LuxException(action, 'action must be a string');
	                this.$apis.set(action, ApiClass);
	                return ApiClass;
	            }

	            if (_.isString(action)) action = { url: action };else action = _.extend({}, action);

	            if (!_.isString(action.url)) throw new LuxException(action, 'action must be an object with url property');

	            var url = action.url,
	                path = url,
	                local = true;
	            if (urlIsAbsolute(url)) {
	                url = urlResolve(url);
	                local = urlIsSameOrigin(url);
	                path = url.pathname;
	            }

	            if (local) {
	                action.baseUrl = '';
	                ApiClass = this.$apis.get(action.baseUrl);
	                if (!ApiClass) ApiClass = this.api('', WebApi);
	            } else {
	                action.baseUrl = url.$base();
	                ApiClass = this.$apis.get(action.baseUrl);
	                if (!ApiClass) ApiClass = this.api(action.baseUrl, RestApi);
	            }

	            action.path = urlJoin(path, action.path);

	            return new ApiClass(this, action);
	        }
	    }, {
	        key: 'id',
	        value: function id(prefix) {
	            return (prefix || 'l') + ++luxId;
	        }
	    }, {
	        key: 'logout',
	        value: function logout(e, url) {
	            e.preventDefault();
	            var api = this.api(url),
	                self = this;

	            api.post().then(function () {
	                if (self.context.POST_LOGOUT_URL) {
	                    self.$window.location.href = self.context.POST_LOGOUT_URL;
	                } else {
	                    self.$window.location.reload();
	                }
	            }, function () {
	                self.messages.error('Error while logging out');
	            });
	        }
	    }, {
	        key: 'csrf',
	        get: function get() {
	            return this.context.csrf;
	        }
	    }, {
	        key: 'user',
	        get: function get() {
	            return this.context.user;
	        }
	    }, {
	        key: 'userToken',
	        get: function get() {
	            return this.context.userToken;
	        }
	    }]);
	    return Lux;
	}();

	var Api = function () {
	    function Api(lux, defaults) {
	        babelHelpers.classCallCheck(this, Api);

	        this.$lux = lux;
	        this.$defaults = defaults;
	    }

	    babelHelpers.createClass(Api, [{
	        key: 'get',
	        value: function get(opts) {
	            return this.request('get', opts);
	        }
	    }, {
	        key: 'post',
	        value: function post(opts) {
	            return this.request('post', opts);
	        }
	    }, {
	        key: 'put',
	        value: function put(opts) {
	            return this.request('put', opts);
	        }
	    }, {
	        key: 'head',
	        value: function head(opts) {
	            return this.request('head', opts);
	        }
	    }, {
	        key: 'delete',
	        value: function _delete(opts) {
	            return this.request('delete', opts);
	        }
	    }, {
	        key: 'paginator',
	        value: function paginator$$() {
	            return new paginator(this);
	        }
	    }, {
	        key: 'httpOptions',
	        value: function httpOptions() {}
	    }, {
	        key: 'request',
	        value: function request(method, opts) {
	            if (!opts) opts = {};
	            // handle urlparams when not an object
	            var $lux = this.$lux,
	                options = {
	                method: method.toLowerCase(),
	                params: _.extend({}, this.params, opts.params),
	                headers: opts.headers || {},
	                url: urlJoin(this.url, opts.path)
	            };

	            if (ENCODE_URL_METHODS.indexOf(options.method) === -1) options.data = opts.data;

	            if (!options.headers.hasOwnProperty('Content-Type')) options.headers['Content-Type'] = 'application/json';

	            this.httpOptions(options);
	            //
	            return $lux.$http(options);
	        }
	    }, {
	        key: 'baseUrl',
	        get: function get() {
	            return this.$defaults.baseUrl;
	        }
	    }, {
	        key: 'url',
	        get: function get() {
	            return urlJoin(this.$defaults.baseUrl, this.$defaults.path);
	        }
	    }, {
	        key: 'params',
	        get: function get() {
	            return this.$defaults.params || {};
	        }
	    }, {
	        key: 'path',
	        get: function get() {
	            return this.$defaults.path;
	        }
	    }]);
	    return Api;
	}();

	var WebApi = function (_Api) {
	    babelHelpers.inherits(WebApi, _Api);

	    function WebApi() {
	        babelHelpers.classCallCheck(this, WebApi);
	        return babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(WebApi).apply(this, arguments));
	    }

	    babelHelpers.createClass(WebApi, [{
	        key: 'httpOptions',
	        value: function httpOptions(options) {
	            var $lux = this.$lux;

	            if ($lux.csrf && NO_CSRF.indexOf(options.method === -1)) options.data = _.extend(options.data || {}, $lux.csrf);
	        }
	    }]);
	    return WebApi;
	}(Api);

	var RestApi = function (_Api2) {
	    babelHelpers.inherits(RestApi, _Api2);

	    function RestApi() {
	        babelHelpers.classCallCheck(this, RestApi);
	        return babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(RestApi).apply(this, arguments));
	    }

	    babelHelpers.createClass(RestApi, [{
	        key: 'httpOptions',
	        value: function httpOptions(options) {
	            var $lux = this.$lux;

	            var token = $lux.userToken;

	            if (token) options.headers.Authorization = 'Bearer ' + token;
	        }
	    }]);
	    return RestApi;
	}(Api);

	// @ngInject
	function $lux ($controllerProvider, $provide, $compileProvider, $filterProvider, $locationProvider, $injector) {

	    lux.$inject = ["$injector", "$location", "$window", "$http", "$log", "$timeout", "$compile", "$rootScope", "luxMessage"];
	    var loading = false,
	        loadingQueue = [],
	        moduleCache = {},
	        plugins = {},
	        providers = {
	        $controllerProvider: $controllerProvider,
	        $compileProvider: $compileProvider,
	        $filterProvider: $filterProvider,
	        $provide: $provide, // other things (constant, decorator, provider, factory, service)
	        $injector: $injector
	    };

	    $locationProvider.html5Mode({
	        enabled: true,
	        requireBase: false,
	        rewriteLinks: false
	    });

	    _.extend(this, providers, {
	        // Required for angular providers
	        plugins: plugins,
	        $get: lux
	    });

	    // @ngInject
	    function lux($injector, $location, $window, $http, $log, $timeout, $compile, $rootScope, luxMessage) {
	        var core = {
	            $injector: $injector,
	            $location: $location,
	            $window: $window,
	            $http: $http,
	            $log: $log,
	            $timeout: $timeout,
	            $compile: $compile,
	            $rootScope: $rootScope,
	            $require: require,
	            require: _require,
	            messages: luxMessage,
	            context: windowContext($window),
	            moduleLoaded: moduleLoaded
	        };
	        return new Lux(core, plugins);
	    }

	    function moduleLoaded(name) {
	        return moduleCache[name] || false;
	    }

	    function _require(libNames, modules, onLoad) {
	        var provider = this;

	        if (arguments.length === 2) {
	            onLoad = modules;
	            modules = null;
	        }
	        if (loading) return loadingQueue.push({
	            libNames: libNames,
	            modules: modules,
	            onLoad: onLoad
	        });

	        if (!_.isArray(libNames)) libNames = [libNames];

	        provider.$require(libNames, execute);

	        function execute() {

	            if (modules) loadModule(modules);

	            onLoad.apply(null, arguments);

	            provider.$timeout(consumeQueue);
	        }

	        function consumeQueue() {
	            var q = loadingQueue.splice(0, 1);
	            if (q.length) {
	                q = q[0];
	                provider.require(q.libNames, q.modules, q.onLoad);
	            }
	        }

	        function loadModule(modules) {
	            if (!_.isArray(modules)) modules = [modules];
	            var moduleFunctions = [];

	            var runBlocks = collectModules(modules, moduleCache, moduleFunctions, []);

	            _.forEach(moduleFunctions, function (moduleFn) {
	                try {
	                    _invokeQueue(moduleFn._invokeQueue);
	                    _invokeQueue(moduleFn._configBlocks);
	                } catch (e) {
	                    if (e.message) e.message += ' while loading ' + moduleFn.name;
	                    throw e;
	                }
	            });

	            function _invokeQueue(queue) {
	                _.forEach(queue, function (args) {
	                    var provider = providers[args[0]],
	                        method = args[1];
	                    if (provider) provider[method].apply(provider, args[2]);else return provider.$log.error("unsupported provider " + args[0]);
	                });
	            }

	            _.forEach(runBlocks, function (fn) {
	                provider.$injector.invoke(fn);
	            });
	        }
	    }
	}

	function collectModules(modules, cache, moduleFunctions, runBlocks) {
	    var moduleFn = void 0;

	    _.forEach(modules, function (moduleName) {
	        if (!cache[moduleName]) {
	            moduleFn = _.module(moduleName);
	            cache[moduleName] = true;
	            runBlocks = collectModules(moduleFn.requires, cache, moduleFunctions, runBlocks);
	            moduleFunctions.push(moduleFn);
	            runBlocks = runBlocks.concat(moduleFn._runBlocks);
	        }
	    });

	    return runBlocks;
	}

	// @ngInject
	function luxMessage ($rootScope, $log) {

	    return new MessageService($rootScope, $log);
	}

	var MessageService = function () {
	    function MessageService($scope, $log) {
	        babelHelpers.classCallCheck(this, MessageService);

	        this.$scope = $scope;
	        this.$log = $log;
	    }

	    babelHelpers.createClass(MessageService, [{
	        key: 'log',
	        value: function log(level, message, opts) {
	            var $log = this.$log;
	            if (!$log[level]) level = 'info';
	            $log[level](message);
	            if (opts && opts.broadcast === false) return;
	            if (!opts) opts = {};
	            opts.text = message;
	            opts.level = level;
	            this.$scope.$broadcast('messageAdded', opts);
	        }
	    }, {
	        key: 'debug',
	        value: function debug(text, opts) {
	            if (arguments.length === 1) opts = { broadcast: false };
	            this.log('debug', text, opts);
	        }
	    }, {
	        key: 'info',
	        value: function info(text, opts) {
	            this.log('info', text, opts);
	        }
	    }, {
	        key: 'success',
	        value: function success(text, opts) {
	            this.log('success', text, opts);
	        }
	    }, {
	        key: 'warn',
	        value: function warn(text, opts) {
	            this.log('warn', text, opts);
	        }
	    }, {
	        key: 'error',
	        value: function error(text, opts) {
	            this.log('error', text, opts);
	        }
	    }, {
	        key: 'clear',
	        value: function clear(id) {
	            this.$scope.$broadcast('messageRemove', id);
	        }
	    }]);
	    return MessageService;
	}();

	function luxPage () {
	    return {
	        restrict: 'A',
	        link: {
	            post: function post(scope, element) {
	                element.addClass('lux');
	            }
	        }
	    };
	}

	var luxModule = _.module('lux', []);

	luxModule.provider('$lux', $lux);

	luxModule.factory('luxMessage', luxMessage);

	luxModule.directive('luxPage', luxPage);

	function luxMessages () {

	    return {
	        restrict: 'AE',
	        replace: true,
	        scope: {},
	        template: messageTpl,
	        link: messages
	    };

	    function pushMessage(scope, message) {
	        message.type = message.level;
	        if (message.type === 'error') message.type = 'danger';
	        scope.messages.push(message);
	    }

	    function messages($scope) {
	        $scope.messages = [];

	        $scope.removeMessage = function ($event, message) {
	            $event.preventDefault();
	            var msgs = $scope.messages;
	            for (var i = 0; i < msgs.length; ++i) {
	                if (msgs[i].$$hashKey === message.$$hashKey) msgs.splice(i, 1);
	            }
	        };

	        $scope.$on('messageAdded', function (e, message) {
	            if (!e.defaultPrevented) pushMessage($scope, message);
	        });

	        $scope.$on('messageRemove', function (e, id) {
	            var messages = [];

	            if (id) _.forEach($scope.messages, function (m) {
	                if (m.id !== id) messages.push(m);
	            });

	            $scope.messages = messages;
	        });
	    }
	}

	var messageTpl = '<div>\n    <div class="alert alert-{{ message.type }}" role="alert" ng-repeat="message in messages">\n        <a href="#" class="close" ng-click="removeMessage($event, message)">&times;</a>\n        <i ng-if="message.icon" ng-class="message.icon"></i>\n        <span ng-bind-html="message.text"></span>\n    </div>\n</div>';

	function querySelector (elem, query) {
	    if (arguments.length === 1 && _.isString(elem)) {
	        query = elem;
	        elem = document;
	    }
	    elem = _.element(elem);
	    if (elem.length && query) return _.element(elem[0].querySelector(query));else return elem;
	}

	var aceTemplate = '<div class="ace-lux">\n<div ng-if="aceHeader" class="ace-lux-header" lux-navbar="aceHeader"></div>\n<div class="ace-lux-editor"></div>\n</div>';

	// load ace with require
	// https://github.com/ajaxorg/ace-builds/issues/35

	// @ngInject
	function luxAce ($lux) {

	    return {
	        restrict: 'EA',
	        require: '?ngModel',
	        link: linkAce
	    };

	    function linkAce(scope, el, attrs, ngModel) {

	        var ace,
	            element,
	            editor,
	            session,
	            text = '',
	            onChangeListener,
	            onBlurListener,
	            opts = _.extend({
	            showGutter: true,
	            theme: 'twilight',
	            mode: 'markdown',
	            tabSize: 4
	        }, $lux.context.ace, scope.$eval(attrs.luxAce));

	        $lux.lazy.require(['ace/ace'], startAce);

	        // Bind to the Model
	        if (ngModel) {
	            ngModel.$formatters.push(function (value) {
	                if (_.isUndefined(value) || value === null) {
	                    return '';
	                } else if (_.isObject(value) || _.isArray(value)) {
	                    return _.toJson(value, 4);
	                }
	                return value;
	            });

	            ngModel.$render = function () {
	                if (session) session.setValue(ngModel.$viewValue);else text = ngModel.$viewValue;
	            };
	        }

	        // Start Ace editor
	        function startAce(_ace) {
	            ace = _ace;
	            ace.config.set("packaged", true);
	            ace.config.set("basePath", require.toUrl("ace"));
	            //
	            element = _.element(aceTemplate);
	            el.after(element).css('display', 'none');
	            element = querySelector(element, '.ace-lux-editor');
	            editor = ace.edit(element[0]);
	            session = editor.getSession();
	            session.setValue(text);
	            updateOptions();

	            el.on('$destroy', function () {
	                editor.session.$stopWorker();
	                editor.destroy();
	            });

	            scope.$watch(function () {
	                return [el[0].offsetWidth, el[0].offsetHeight];
	            }, function () {
	                editor.resize();
	                editor.renderer.updateFull();
	            }, true);
	        }

	        function updateOptions() {

	            // unbind old change listener
	            session.removeListener('change', onChangeListener);
	            onChangeListener = onChange(opts.onChange);
	            session.on('change', onChangeListener);

	            // unbind old blur listener
	            editor.removeListener('blur', onBlurListener);
	            onBlurListener = onBlur(opts.onBlur);
	            session.on('blur', onBlurListener);

	            setOptions();
	        }

	        function onChange(callback) {

	            return function (e) {
	                var newValue = session.getValue();

	                if (ngModel && newValue !== ngModel.$viewValue &&
	                // HACK make sure to only trigger the apply outside of the
	                // digest loop 'cause ACE is actually using this callback
	                // for any text transformation !
	                !scope.$$phase && !scope.$root.$$phase) {
	                    scope.$evalAsync(function () {
	                        ngModel.$setViewValue(newValue);
	                    });
	                }

	                executeUserCallback(callback, e);
	            };
	        }

	        function onBlur(callback) {
	            return function () {
	                executeUserCallback(callback);
	            };
	        }

	        function executeUserCallback(callback) {
	            if (_.isDefined(callback)) {
	                var args = Array.prototype.slice.call(arguments, 1);

	                scope.$evalAsync(function () {
	                    callback.apply(editor, args);
	                });
	            }
	        }

	        function setOptions() {
	            editor.setTheme('ace/theme/' + opts.theme);
	            session.setMode('ace/mode/' + opts.mode);
	            var options = _.extend({}, opts);
	            delete options.theme;
	            delete options.mode;
	            editor.setOptions(options);

	            // commands
	            if (_.isDefined(opts.disableSearch) && opts.disableSearch) {
	                editor.commands.addCommands([{
	                    name: 'unfind',
	                    bindKey: {
	                        win: 'Ctrl-F',
	                        mac: 'Command-F'
	                    },
	                    exec: function exec() {
	                        return false;
	                    },
	                    readOnly: true
	                }]);
	            }
	        }
	    }
	}

	function capitalize (str) {
	    return str.charAt(0).toUpperCase() + str.slice(1);
	}

	// @ngInject
	function luxCrumbs ($location) {
	    CrumbsCtrl.$inject = ["$scope"];
	    return {
	        restrict: 'AE',
	        replace: true,
	        template: crumbsTemplate,
	        controller: CrumbsCtrl
	    };

	    // @ngInject
	    function CrumbsCtrl($scope) {
	        $scope.steps = crumbs($location);
	    }
	}

	function crumbs(loc) {
	    var steps = [],
	        path = loc.path(),
	        last = last = {
	        label: 'Home',
	        href: '/'
	    };

	    steps.push(last);

	    path.split('/').forEach(function (name) {
	        if (name) {
	            last = {
	                label: name.split(/[-_]+/).map(capitalize).join(' '),
	                href: urlJoin(last.href, name)
	            };
	            steps.push(last);
	        }
	    });
	    steps[steps.length - 1].last = true;

	    return steps;
	}

	var crumbsTemplate = '<ol class="breadcrumb">\n    <li ng-repeat="step in steps" ng-class="{active: step.last}">\n        <a ng-if="!step.last" href="{{step.href}}">{{step.label}}</a>\n        <span ng-if="step.last">{{step.label}}</span>\n    </li>\n</ol>';

	function luxYear () {
	    return {
	        restrict: 'AE',
	        link: function link(scope, element) {
	            var dt = new Date();
	            element.html(dt.getFullYear() + '');
	        }
	    };
	}

	// @ngInject
	function luxFullpage ($window) {

	    return {
	        restrict: 'AE',

	        link: function link(scope, element, attrs) {
	            var opts = scope.$eval(attrs.luxFullpage) || {},
	                offset = +(opts.offset || 0),
	                height = $window.innerHeight - offset,
	                watch = opts.watch;

	            element.css('min-height', height + 'px');

	            if (watch) {
	                scope.$watch(function () {
	                    return $window.innerHeight - offset;
	                }, function (value) {
	                    element.css('min-height', value + 'px');
	                });
	            }
	        }
	    };
	}

	var cmsModule = _.module('lux.cms', ['lux']);

	cmsModule.directive('luxMessages', luxMessages);
	cmsModule.directive('luxAce', luxAce);
	cmsModule.directive('luxCrumbs', luxCrumbs);
	cmsModule.directive('luxYear', luxYear);
	cmsModule.directive('luxFullpage', luxFullpage);

	function luxFormConfig () {
	    var _this = this;

	    var formMap = {},
	        wrapperMap = {},
	        // container of Html wrappers for form elements
	    actionMap = {},
	        // container of actions on a form
	    successHooks = {},
	        // collection of handlers invoked on successful submit
	    errors = {},
	        tagMap = {
	        date: 'input',
	        datetime: 'input',
	        email: 'input',
	        hidden: 'input',
	        month: 'input',
	        number: 'input',
	        password: 'input',
	        search: 'input',
	        tel: 'input',
	        text: 'input',
	        time: 'input',
	        url: 'input',
	        week: 'input'
	    };

	    var formCount = 1;

	    _.extend(this, {
	        setType: setType,
	        getType: getType,
	        setWrapper: setWrapper,
	        getWrapper: getWrapper,
	        getTag: getTag,
	        setTag: setTag,
	        getAction: getAction,
	        setAction: setAction,
	        onSuccess: onSuccess,
	        error: error,
	        id: formid,
	        // Required for angular providers
	        $get: function $get() {
	            return _this;
	        }
	    });

	    function formid() {
	        return 'lf' + ++formCount;
	    }

	    function setType(options) {
	        if (_.isObject(options) && _.isString(options.name)) {
	            var formName = options.form || 'default',
	                form = formMap[formName];

	            if (!form) formMap[formName] = form = {};

	            if (formName !== 'default') options = _.extend({}, formMap.default[options.name], options);

	            form[options.name] = options;
	            return options;
	        } else {
	            throw Error('An object with attribute name is required.\n                Given: ' + JSON.stringify(arguments) + '\n                ');
	        }
	    }

	    function getType(name, formName) {
	        formName = formName || 'default';
	        var form = formMap[formName];
	        if (!form) throw Error('Form ' + formName + ' is not available');
	        name = getTag(name);
	        return form[name];
	    }

	    function setWrapper(wrapper) {
	        if (_.isObject(wrapper) && _.isString(wrapper.name) && _.isFunction(wrapper.template)) {
	            wrapperMap[wrapper.name] = wrapper;
	        }
	    }

	    function getWrapper(name) {
	        return wrapperMap[name];
	    }

	    function setTag(type, tag) {
	        tagMap[type] = tag;
	    }

	    function getTag(type) {
	        return tagMap[type] || type;
	    }

	    function getAction(type) {
	        return actionMap[type];
	    }

	    function setAction(type, action) {
	        actionMap[type] = action;
	    }

	    function onSuccess(type, hook) {
	        if (arguments.length === 2) {
	            successHooks[type] = hook;
	            return this;
	        } else return successHooks[type] || successHooks['default'];
	    }

	    function error(name, message) {
	        if (arguments.length === 2) {
	            errors[name] = message;
	            return this;
	        } else {
	            var obj = name.$error,
	                errorHandler;
	            for (var key in obj) {
	                if (obj.hasOwnProperty(key) && obj[key]) {
	                    errorHandler = errors[key];
	                    if (errorHandler) break;
	                }
	            }

	            if (_.isFunction(errorHandler)) return errorHandler(name);else return errorHandler;
	        }
	    }
	}

	function reversemerge (target, defaults) {
	    if (!_.isObject(target)) return;

	    _.forEach(defaults, function (value, key) {
	        if (!target.hasOwnProperty(key)) target[key] = value;
	    });

	    return target;
	}

	var LuxComponent = function () {
	    function LuxComponent($lux) {
	        babelHelpers.classCallCheck(this, LuxComponent);

	        this.$lux = $lux;
	        this.$id = $lux.id();
	    }

	    babelHelpers.createClass(LuxComponent, [{
	        key: 'addMessages',
	        value: function addMessages(messages, level) {
	            if (!level) level = 'info';
	            var $lux = this.$lux,
	                opts = { rel: this.$id };

	            if (!_.isArray(messages)) messages = [messages];
	            _.forEach(messages, function (message) {
	                $lux.messages.log(level, message, opts);
	            });
	        }
	    }, {
	        key: '$compile',
	        get: function get() {
	            return this.$lux.$compile;
	        }
	    }, {
	        key: '$injector',
	        get: function get() {
	            return this.$lux.$injector;
	        }
	    }]);
	    return LuxComponent;
	}();

	// @ngInject
	function luxForm($lux, $log, luxFormConfig) {

	    FormController.$inject = ["$scope"];
	    return {
	        restrict: 'AE',
	        replace: true,
	        transclude: true,
	        scope: {
	            'json': '=?',
	            'model': '=?'
	        },
	        template: formTemplate,
	        controller: FormController,
	        link: {
	            post: postLink
	        }
	    };

	    function formTemplate(el, attrs) {
	        var href = attrs.href;

	        if (href && !attrs.json) {
	            return $lux.api(href).get().then(function (data) {
	                attrs.json = data;
	                return formTemplate(el, attrs);
	            }, function (msg) {
	                $lux.messages.error(msg);
	            });
	        }

	        var form_id = attrs.id || 'form',
	            inner = innerTemplate(form_id);

	        return '<form class="lux-form" name="' + form_id + '" role="form" novalidate>\n' + inner + '\n<div ng-transclude></div>\n</form>';
	    }

	    // ngInject
	    function FormController($scope) {
	        $scope.model = {}; // model values
	        $scope.fields = {};
	        $scope.info = new Form($scope, $lux, $log, luxFormConfig, $scope.json);
	        $scope.field = $scope.info;
	    }

	    function postLink($scope) {
	        var info = $scope.info,
	            action = info.action;

	        if (!action || action.action != 'update') return;

	        var api = $lux.api(action);
	        $scope.form.$pending = true;
	        api.get().then(success, failure);

	        function success(response) {
	            $scope.form.$pending = false;
	            var data = response.data;
	            _.forEach(data, function (value, key) {
	                $scope.model[key] = value.id || value;
	            });
	        }

	        function failure() {
	            $scope.form.$pending = false;
	        }
	    }
	}

	// @ngInject
	function luxField($log, $lux, luxFormConfig) {
	    FieldController.$inject = ["$scope"];
	    var cfg = luxFormConfig;

	    return {
	        restrict: 'AE',
	        require: '?^luxForm',
	        scope: {
	            info: '=',
	            model: '=',
	            form: '=',
	            field: '='
	        },
	        controller: FieldController,
	        link: linkField
	    };

	    // @ngInject
	    function FieldController($scope) {
	        var field = $scope.field,
	            tag = field.tag || cfg.getTag(field.type);

	        if (!tag) return $log.error('Could not find a tag for field');

	        field.id = field.id || cfg.id();
	        field.tag = tag;

	        var type = cfg.getType(field.tag);

	        if (!type) return $log.error('No field type for ' + field.tag);

	        if (!type.group) {
	            if (!field.name) return $log.error('Field with no name attribute in lux-form');
	            $scope.field = field = new Field($scope, $lux, $log, cfg, field);
	            $scope.info.fields[field.name] = field;
	        }

	        mergeOptions(field, type.defaultOptions, $scope);
	        field.fieldType = type;
	    }

	    function linkField(scope, el) {
	        var field = scope.field,
	            fieldType = field.fieldType,
	            template,
	            w;

	        if (!fieldType) return;

	        template = fieldType.template || '';

	        if (_.isFunction(template)) template = template(field);

	        var children = field.children;

	        if (_.isArray(children) && children.length) {
	            var inner = innerTemplate('form');
	            if (template) {
	                var tel = _.element(template);
	                tel.append(inner);
	                template = asHtml(tel);
	            } else template = inner;
	        }

	        _.forEach(fieldType.wrapper, function (wrapper) {
	            w = cfg.getWrapper(wrapper);
	            if (w) template = w.template(template) || template;else $log.error('Could not locate lux-form wrapper "' + wrapper + '" in "' + field.name + '" field');
	        });

	        el.html(asHtml(template));
	        var compileHtml = fieldType.compile || compile;
	        compileHtml($lux, el.contents(), scope);
	    }

	    function mergeOptions(field, defaults, $scope) {
	        if (_.isFunction(defaults)) defaults = defaults(field, $scope);
	        reversemerge(field, defaults);
	    }

	    // sort-of stateless util functions
	    function asHtml(el) {
	        var wrapper = _.element('<a></a>');
	        return wrapper.append(el).html();
	    }

	    function compile(lazy, html, scope) {
	        lazy.$compile(html)(scope);
	    }
	}

	function innerTemplate(form_id) {
	    return '<lux-field ng-repeat="child in field.children"\nfield="child"\nmodel="model"\ninfo="info"\nform="' + form_id + '">\n</lux-field>';
	}

	var FormElement = function (_LuxComponent) {
	    babelHelpers.inherits(FormElement, _LuxComponent);

	    function FormElement($scope, $lux, $log, $cfg, field) {
	        babelHelpers.classCallCheck(this, FormElement);

	        var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(FormElement).call(this, $lux));

	        _this.$scope = $scope;
	        _this.$lux = $lux;
	        _this.$cfg = $cfg;
	        _this.$log = $log;
	        var directives = [];
	        _.forEach(field, function (value, key) {
	            if (isDirective(key)) directives.push(key + '=\'' + value + '\'');else _this[key] = value;
	        });
	        _this.directives = directives.join(' ');
	        return _this;
	    }

	    babelHelpers.createClass(FormElement, [{
	        key: '$form',
	        get: function get() {
	            return this.$scope.form;
	        }
	    }, {
	        key: 'model',
	        get: function get() {
	            return this.$scope.model;
	        }
	    }]);
	    return FormElement;
	}(LuxComponent);

	var Form = function (_FormElement) {
	    babelHelpers.inherits(Form, _FormElement);

	    function Form() {
	        babelHelpers.classCallCheck(this, Form);
	        return babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(Form).apply(this, arguments));
	    }

	    babelHelpers.createClass(Form, [{
	        key: 'setSubmited',
	        value: function setSubmited() {
	            this.$form.$setSubmitted();
	            this.$form.$pending = true;
	            this.$lux.messages.clear(this.id);
	            _.forEach(this.fields, function (field) {
	                delete field.server_message;
	                delete field.server_error;
	            });
	        }
	    }, {
	        key: 'addMessages',
	        value: function addMessages(messages, level) {
	            var fields = this.fields,
	                formMessage = [];
	            if (!_.isArray(messages)) messages = [messages];

	            _.forEach(messages, function (message) {
	                if (message.field && fields[message.field]) {
	                    if (level === 'error') {
	                        fields[message.field].server_error = message.message;
	                        fields[message.field].ngField.$invalid = true;
	                    } else fields[message.field].server_message = message.message;
	                } else formMessage.push(message);
	            });

	            babelHelpers.get(Object.getPrototypeOf(Form.prototype), 'addMessages', this).call(this, formMessage, level);
	        }
	    }, {
	        key: 'fields',
	        get: function get() {
	            return this.$scope.fields;
	        }
	    }]);
	    return Form;
	}(FormElement);

	// Logic and data for a form Field


	var Field = function (_FormElement2) {
	    babelHelpers.inherits(Field, _FormElement2);

	    function Field() {
	        babelHelpers.classCallCheck(this, Field);
	        return babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(Field).apply(this, arguments));
	    }

	    babelHelpers.createClass(Field, [{
	        key: '$click',
	        value: function $click($event) {
	            var action = this.$cfg.getAction(this.type);
	            if (action) action.call(this, $event);
	        }
	    }, {
	        key: 'error',
	        get: function get() {
	            var ngField = this.ngField;
	            if (ngField && this.displayStatus && ngField.$invalid) {
	                var msg = this.$cfg.error(ngField);
	                return this.server_error || msg || 'Not a valid value';
	            }
	        }
	    }, {
	        key: 'success',
	        get: function get() {
	            if (this.displayStatus && !this.error) return true;
	        }
	    }, {
	        key: 'displayStatus',
	        get: function get() {
	            if (this.disabled || this.readonly) return false;
	            var ngField = this.ngField;
	            return ngField && (this.$form.$submitted || ngField.$dirty);
	        }
	    }, {
	        key: 'ngField',
	        get: function get() {
	            return this.$scope.form[this.name];
	        }
	    }, {
	        key: 'info',
	        get: function get() {
	            return this.$scope.info;
	        }
	    }]);
	    return Field;
	}(FormElement);

	function isDirective(key) {
	    var bits = key.split('-');
	    if (bits.length === 2) return true;
	}

	function defaultPlaceholder(field) {
	    return field.label || field.title || field.name;
	}

	function selectOptions(field) {
	    var options = field.options;
	    delete field.options;
	    if (_.isString(options)) {
	        // Assume a url
	        field.$lux.api(options).get().then(function (response) {
	            if (response.status === 200) parseOptions(field, response.data);
	        });
	    } else {
	        parseOptions(field, options);
	    }
	}

	function parseOptions(field, items, objParser) {
	    if (!_.isArray(items)) items = [];
	    field.options = items.map(function (opt) {
	        if (_.isArray(opt)) {
	            opt = {
	                value: opt[0],
	                label: opt[1] || opt[0]
	            };
	        } else if (_.isObject(opt)) opt = objParser ? objParser(opt) : opt;else opt = { value: opt, label: '' + opt };
	        return opt;
	    });
	}

	// @ngInject
	function luxRemote ($lux) {

	    return {
	        restrict: 'A',
	        link: link
	    };

	    function link(scope, element, attrs) {
	        var remote = attrs.luxRemote;
	        if (_.isString(remote)) remote = _.fromJson(remote);
	        var field = scope.field;
	        if (!field) scope.field = field = {};
	        field.paginator = $lux.api(remote).paginator();
	        remoteOptions(field);
	    }
	}

	function compileUiSelect(lazy, html, scope) {

	    lazy.require(['angular-ui-select', 'angular-sanitize'], ['ui.select', 'ngSanitize'], function () {
	        html = lazy.$compile(html)(scope);
	    });
	}

	function remoteOptions(field) {
	    var params = field.paginator.api.$defaults,
	        id = params.id_field,
	        repr = params.repr_field;

	    getData();

	    function getData() {
	        var placeholder = field.placeholder;
	        field.placeholder = 'Loading data...';

	        field.paginator.getData(function (data) {
	            field.placeholder = placeholder;
	            parseOptions(field, data, parseEntry);
	        });
	    }

	    function parseEntry(entry) {
	        return {
	            value: entry[id],
	            label: entry[repr]
	        };
	    }
	}

	// Set default types
	function formDefaults (ngModule) {
	    addTypes.$inject = ["luxFormConfigProvider"];
	    ngModule.config(addTypes);

	    // @ngInject
	    function addTypes(luxFormConfigProvider) {
	        var p = luxFormConfigProvider;

	        // Inputs
	        p.setType({
	            name: 'input',
	            template: inputTpl,
	            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
	            defaultOptions: function defaultOptions(field) {
	                return {
	                    title: field.name,
	                    placeholder: defaultPlaceholder(field),
	                    labelSrOnly: field.showLabels === false || field.type === 'hidden',
	                    value: ''
	                };
	            }
	        });

	        // Checkbox
	        p.setType({
	            name: 'checkbox',
	            template: checkboxTpl
	        });

	        // Radio
	        p.setType({
	            name: 'radio',
	            template: radioTpl,
	            wrapper: ['bootstrapLabel', 'bootstrapStatus']
	        });

	        // Select
	        p.setType({
	            name: 'select',
	            template: selectTpl,
	            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
	            defaultOptions: function defaultOptions(field) {
	                return {
	                    placeholder: defaultPlaceholder(field),
	                    options: selectOptions(field)
	                };
	            }
	        });

	        // UI-Select
	        p.setType({
	            name: 'ui-select',
	            template: uiSelectTpl,
	            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
	            defaultOptions: function defaultOptions(field) {
	                return {
	                    placeholder: defaultPlaceholder(field),
	                    options: selectOptions(field)
	                };
	            },
	            compile: compileUiSelect
	        });

	        // Textarea
	        p.setType({
	            name: 'textarea',
	            template: textareaTpl,
	            wrapper: ['bootstrapLabel', 'bootstrapStatus'],
	            defaultOptions: function defaultOptions(field) {
	                return {
	                    placeholder: defaultPlaceholder(field),
	                    ngModelAttrs: {
	                        rows: { attribute: 'rows' },
	                        cols: { attribute: 'cols' }
	                    }
	                };
	            }
	        });

	        // Button / Submit
	        p.setType({
	            name: 'button',
	            template: buttonTpl,
	            defaultOptions: function defaultOptions(field) {
	                return {
	                    label: field.name,
	                    type: 'submit',
	                    value: field.name
	                    //disabled: "form.$invalid"
	                };
	            }
	        });

	        // Fieldset
	        p.setType({
	            name: 'fieldset',
	            template: fieldsetTpl,
	            group: true
	        });

	        // Div
	        p.setType({
	            name: 'div',
	            group: true
	        });
	    }
	}

	function inputTpl(field) {
	    return '<input class="form-control" \nid="' + field.id + '"\nname="' + field.name + '"\ntype="' + field.type + '"\nvalue="' + field.value + '"\ntitle="' + field.title + '"\nplaceholder="' + field.placeholder + '"\n' + field.directives + '\nng-model="model[\'' + field.name + '\']"\nng-required="field.required"\nng-readonly="field.readonly"\nng-disabled="' + field.disabled + '"\nng-minlength="field.minlength"\nng-maxlength="field.maxlength"\n>';
	}

	function selectTpl(field) {
	    return '<select class="form-control"\nid="' + field.id + '"\nname="' + field.name + '"\n' + field.directives + '\nng-model="model[\'' + field.name + '\']"\nng-options="option.label for option in field.options track by option.value"\nng-required="field.required"\nng-readonly="field.readonly"\nng-disabled="' + field.disabled + '"\n>\n</select>';
	}

	function textareaTpl(field) {
	    return '<textarea class="form-control"\nid="' + field.id + '"\nname="' + field.name + '"\nplaceholder="' + field.placeholder + '"\n' + field.directives + '\nng-model="model[\'' + field.name + '\']"\nng-required="field.required"\nng-readonly="field.readonly"\nng-disabled="field.disabled">\n"' + field.value + '"\n</textarea>';
	}

	function checkboxTpl(field) {
	    return '<div class="checkbox">\n<label>\n<input type="checkbox"\nng-model="model[\'' + field.name + '\']">\n' + field.label + '\n</label>\n</div>';
	}

	var radioTpl = '\n<div class="radio-group">\n  <div ng-repeat="(key, option) in to.options" ng-class="{ \'radio\': !to.inline, \'radio-inline\': to.inline }">\n    <label>\n      <input type="radio"\n             id="{{id + \'_\'+ $index}}"\n             tabindex="0"\n             ng-value="option[to.valueProp || \'value\']"\n             ng-model="model[field.name]">\n      {{option[to.labelProp || \'name\']}}\n    </label>\n  </div>\n</div>\n';

	function fieldsetTpl(field) {
	    var legend = field.legend || '';
	    if (legend) legend = '<legend>' + legend + '</legend>';
	    return '<fieldset>' + legend + '</fieldset>';
	}

	function buttonTpl(field) {
	    return '<button name="' + field.name + '"\nclass="btn btn-default"\nng-disabled="field.disabled"\ntype="' + field.type + '"\nng-click="field.$click($event)"\n>' + field.label + '</button>';
	}

	function uiSelectTpl(field) {
	    return '<ui-select\nid="' + field.id + '"\nname="' + field.name + '"\n' + field.directives + '\ntheme="bootstrap"\nng-model="model[\'' + field.name + '\']"\nng-required="field.required"\nng-readonly="field.readonly"\nng-disabled="' + field.disabled + '"\n>\n<ui-select-match placeholder="' + field.placeholder + '">{{$select.selected.label}}</ui-select-match>\n<ui-select-choices repeat="item.value as item in field.options | filter: $select.search">\n  <div ng-bind-html="item.label | highlight: $select.search"></div>\n  <small ng-if="item.description" ng-bind-html="item.description | highlight: $select.search"></small>\n</ui-select-choices>\n</ui-select>';
	}

	function formWrappers (ngModule) {
	    addWrappers.$inject = ["luxFormConfigProvider"];
	    ngModule.config(addWrappers);

	    // @ngInject
	    function addWrappers(luxFormConfigProvider) {
	        var p = luxFormConfigProvider;

	        p.setWrapper({
	            name: 'bootstrapLabel',
	            template: labelTpl
	        });

	        p.setWrapper({
	            name: 'bootstrapStatus',
	            template: statusTpl
	        });
	    }
	}

	var labelTpl = function labelTpl(inner) {
	    return '<label for="{{field.id}}" class="control-label {{field.labelSrOnly ? \'sr-only\' : \'\'}}" ng-if="field.label">\n    {{field.label}}\n    {{field.required ? \'*\' : \'\'}}\n  </label>\n  ' + inner;
	};

	var statusTpl = function statusTpl(inner) {
	    return '<div class="form-group" ng-class="{\'has-error\': field.error, \'has-success\': field.success}">\n' + inner + '\n<p ng-if="field.error" class="text-danger error-block">{{ field.error }}</p>\n</div>';
	};

	function formActions (ngModule) {

	    // @ngInject
	    addActions.$inject = ["luxFormConfigProvider"];
	    ngModule.config(addActions);

	    function addActions(luxFormConfigProvider) {
	        var cfg = luxFormConfigProvider;

	        cfg.setAction('submit', submitForm);

	        cfg.onSuccess('default', defaultOnSuccess);
	    }
	}

	function submitForm(e) {

	    var form = this.$form,
	        $lux = this.$lux,
	        $cfg = this.$cfg,
	        info = this.info,
	        action = info.action;

	    if (!action) return;

	    e.preventDefault();
	    e.stopPropagation();

	    var api = $lux.api(action);

	    // Flag the form as submitted
	    info.setSubmited();
	    //
	    // Invalid?
	    if (form.$invalid) form.$setDirty();
	    // return this.$lux.messages.info('Invalid form - not submitting');

	    var ct = (info.enctype || '').split(';')[0],
	        method = info.method || 'post',
	        options = { data: info.model };

	    if (ct === 'application/x-www-form-urlencoded' || ct === 'multipart/form-data') options.headers = {
	        'content-type': undefined
	    };

	    api.request(method, options).then(success, failure);

	    function success(response) {
	        form.$pending = false;
	        var hook = $cfg.onSuccess(info.resultHandler);
	        hook(response, info);
	    }

	    function failure(response) {
	        form.$pending = false;
	        var data = response.data || {},
	            errors = data.errors;

	        if (!errors) {
	            errors = data.message;
	            if (!errors) {
	                var status = response.status || data.status || 501;
	                errors = 'Response error (' + status + ')';
	            }
	        }
	        info.addMessages(errors, 'error');
	    }
	}

	function defaultOnSuccess(response, form) {
	    var data = response.data,
	        messages = data.messages;

	    if (!messages) {
	        messages = data.message;
	        if (!messages) {
	            if (response.status === 201) messages = 'Successfully created';else messages = 'Successfully updated';
	        }
	    }

	    form.addMessages(messages);
	}

	function formMessages (ngModule) {
	    errorMessages.$inject = ["luxFormConfigProvider"];
	    ngModule.config(errorMessages);

	    // @ngInject
	    function errorMessages(luxFormConfigProvider) {
	        var p = luxFormConfigProvider;

	        p.error('minlength', function (field) {
	            return field.$name + ' length should be more than ' + field.$viewValue.length;
	        });

	        p.error('maxlength', function (field) {
	            return field.$name + ' length should be less than ' + field.$viewValue.length;
	        });

	        p.error('required', function (field) {
	            return field.$name + ' is required';
	        });
	    }
	}

	// @ngInject
	function runForm ($window, luxFormConfig) {

	    luxFormConfig.onSuccess('redirect', function (response, form) {
	        $window.location.href = form.redirectTo || '/';
	    }).onSuccess('reload', function () {
	        $window.location.reload();
	    });
	}

	// lux.form module
	var luxFormModule = _.module('lux.form', ['lux']);

	luxFormModule.provider('luxFormConfig', luxFormConfig);

	luxFormModule.directive('luxForm', luxForm);
	luxFormModule.directive('luxField', luxField);
	luxFormModule.directive('luxRemote', luxRemote);

	formDefaults(luxFormModule);

	formWrappers(luxFormModule);

	formActions(luxFormModule);

	formMessages(luxFormModule);

	luxFormModule.run(runForm);

	var linkTemplate = '<a ng-href="{{link.href}}" title="{{link.title}}" ng-click="links.click($event, link)"\nng-attr-target="{{link.target}}" ng-class="link.klass" bs-tooltip="tooltip">\n<span ng-if="link.left" class="left-divider"></span>\n<i ng-if="link.icon" class="{{link.icon}}"></i>\n<span>{{link.label || link.name}}</span>\n<span ng-if="link.right" class="right-divider"></span></a>';

	var navbarTemplate = '<nav ng-attr-id="{{navbar.id}}" class="navbar navbar-{{navbar.theme}}"\nng-class="{\'navbar-fixed-top\':navbar.fixed, \'navbar-static-top\':navbar.top}"\nng-style="navbar.style" role="navigation">\n    <div ng-class="navbar.container">\n        <div class="navbar-header">\n            <button ng-if="navbar.toggle" type="button" class="navbar-toggle" ng-click="navbar.isCollapsed = !navbar.isCollapsed">\n                <span class="sr-only">Toggle navigation</span>\n                <span class="icon-bar"></span>\n                <span class="icon-bar"></span>\n                <span class="icon-bar"></span>\n            </button>\n            <ul ng-if="navbar.itemsLeft" class="nav navbar-nav navbar-left">\n                <li ng-repeat="link in navbar.itemsLeft" ng-class="{active:links.activeLink(link)}" lux-link></li>\n            </ul>\n            <a ng-if="navbar.brandImage" href="{{navbar.url}}" class="navbar-brand" target="{{navbar.target}}">\n                <img ng-src="{{navbar.brandImage}}" alt="{{navbar.brand || \'brand\'}}">\n            </a>\n            <a ng-if="!navbar.brandImage && navbar.brand" href="{{navbar.url}}" class="navbar-brand" target="{{navbar.target}}">\n                {{navbar.brand}}\n            </a>\n        </div>\n        <nav class="navbar-collapse"\n             uib-collapse="navbar.isCollapsed"\n             expanding="navbar.expanding()"\n             expanded="navbar.expanded()"\n             collapsing="navbar.collapsing()"\n             collapsed="navbar.collapsed()">\n            <ul ng-if="navbar.items" class="nav navbar-nav navbar-left">\n                <li ng-repeat="link in navbar.items" ng-class="{active:links.activeLink(link)}" lux-link></li>\n            </ul>\n            <ul ng-if="navbar.itemsRight" class="nav navbar-nav navbar-right">\n                <li ng-repeat="link in navbar.itemsRight" ng-class="{active:links.activeLink(link)}" lux-link></li>\n            </ul>\n        </nav>\n    </div>\n</nav>';

	var sidebarTemplate = '<lux-navbar class="sidebar-navbar" ng-class="{\'sidebar-open-left\': navbar.left, \'sidebar-open-right\': navbar.right}"></lux-navbar>\n<aside ng-repeat="sidebar in sidebars"\n       class="sidebar sidebar-{{ sidebar.position }}"\n       ng-attr-id="{{ sidebar.id }}"\n       ng-class="{\'sidebar-fixed\': sidebar.fixed, \'sidebar-open\': sidebar.open, \'sidebar-close\': sidebar.closed}" bs-collapse>\n    <div class="nav-panel">\n        <div ng-if="sidebar.user">\n            <div ng-if="sidebar.user.avatar_url" class="pull-{{ sidebar.position }} image">\n                <img ng-src="{{sidebar.user.avatar_url}}" alt="User Image" />\n            </div>\n            <div class="pull-left info">\n                <p>{{ sidebar.infoText }}</p>\n                <a ng-attr-href="{{sidebar.user.username ? \'/\' + sidebar.user.username : \'#\'}}">{{sidebar.user.name}}</a>\n            </div>\n        </div>\n    </div>\n    <ul class="sidebar-menu">\n        <li ng-if="section.name" ng-repeat-start="section in sidebar.sections" class="header">\n            {{section.name}}\n        </li>\n        <li ng-repeat-end ng-repeat="link in section.items" class="treeview"\n        ng-class="{active:links.activeLink(link)}" ng-include="\'subnav\'"></li>\n    </ul>\n</aside>\n<div class="sidebar-page" ng-class="{\'sidebar-open-left\': navbar.left, \'sidebar-open-right\': navbar.right}" ng-click="closeSidebars()">\n    <div class="overlay"></div>\n</div>\n\n<script type="text/ng-template" id="subnav">\n    <a ng-href="{{link.href}}" ng-attr-title="{{link.title}}" ng-click="sidebar.menuCollapse($event)">\n        <i ng-if="link.icon" class="{{link.icon}}"></i>\n        <span>{{link.name}}</span>\n        <i ng-if="link.subitems" class="fa fa-angle-left pull-right"></i>\n    </a>\n    <ul class="treeview-menu" ng-class="{active:links.activeSubmenu(link)}" ng-if="link.subitems">\n        <li ng-repeat="link in link.subitems" ng-class="{active:links.activeLink(link)}" ng-include="\'subnav\'">\n        </li>\n    </ul>\n</script>';

	var navbarDefaults = {
	    theme: 'default',
	    search_text: '',
	    // Navigation place on top of the page (add navbar-static-top class to navbar)
	    // nabar2 it is always placed on top
	    top: false,
	    // Fixed navbar
	    fixed: false,
	    search: false,
	    url: '/',
	    target: '_self',
	    toggle: true,
	    fluid: true,
	    expanding: noop,
	    expanded: noop,
	    collapsing: noop,
	    collapsed: noop,
	    isCollapsed: true
	};

	var sidebarDefaults = {
	    open: false,
	    toggleName: 'Menu',
	    infoText: 'Signed in as'
	};

	// @ngInject
	function link($location) {

	    return {
	        click: click,
	        activeLink: activeLink,
	        activeSubmenu: activeSubmenu
	    };

	    function click(e, link) {
	        if (link.action) {
	            var func = link.action;
	            if (func) func(e, link.href, link);
	        }
	    }

	    // Check if a url is active
	    function activeLink(url) {
	        var loc;
	        if (url)
	            // Check if any submenus/sublinks are active
	            if (url.subitems && url.subitems.length > 0) {
	                if (exploreSubmenus(url.subitems)) return true;
	            }
	        url = _.isString(url) ? url : url.href || url.url;
	        if (!url) return;
	        if (urlIsAbsolute(url)) loc = $location.absUrl();else loc = $location.path();
	        var rest = loc.substring(url.length),
	            base = url.length < loc.length ? false : loc.substring(0, url.length),
	            folder = url.substring(url.length - 1) === '/';
	        return base === url && (folder || rest === '' || rest.substring(0, 1) === '/');
	    }

	    function activeSubmenu(url) {
	        var active = false;

	        if (url.href && url.href === '#' && url.subitems.length > 0) {
	            active = exploreSubmenus(url.subitems);
	        } else {
	            active = false;
	        }
	        return active;
	    }

	    // recursively loops through arrays to
	    // find url match
	    function exploreSubmenus(array) {
	        for (var i = 0; i < array.length; i++) {
	            if (array[i].href === $location.path()) {
	                return true;
	            } else if (array[i].subitems && array[i].subitems.length > 0) {
	                if (exploreSubmenus(array[i].subitems)) return true;
	            }
	        }
	    }
	}

	// @ngInject
	function navbar(luxNavBarDefaults) {

	    return luxNavbar;

	    function luxNavbar(opts) {
	        var navbar = _.extend({}, luxNavBarDefaults, opts);

	        if (!navbar.url) navbar.url = '/';

	        navbar.container = navbar.fluid ? 'container-fluid' : 'container';

	        return navbar;
	    }
	}

	// @ngInject
	function sidebar(luxSidebarDefaults) {

	    return sidebar;

	    function sidebar(opts) {
	        opts || (opts = {});

	        var sidebars = [];

	        if (opts.left) add(opts.left, 'left');
	        if (opts.right) add(opts.right, 'right');
	        if (!sidebars.length) add(opts, 'left');

	        return sidebars;

	        // Add a sidebar (left or right position)
	        function add(sidebar, position) {
	            sidebar = _.extend({
	                position: position,
	                menuCollapse: menuCollapse
	            }, luxSidebarDefaults, sidebar);

	            if (sidebar.sections) {
	                sidebars.push(sidebar);
	                return sidebar;
	            }
	        }
	    }

	    function menuCollapse($event) {
	        // Get the clicked link, the submenu and sidebar menu
	        var item = _.element($event.currentTarget || $event.srcElement),
	            submenu = item.next();

	        // If the menu is not visible then close all open menus
	        if (submenu.hasClass('active')) {
	            item.removeClass('active');
	            submenu.removeClass('active');
	        } else {
	            var itemRoot = item.parent().parent();
	            itemRoot.find('ul').removeClass('active');
	            itemRoot.find('li').removeClass('active');

	            item.parent().addClass('active');
	            submenu.addClass('active');
	        }
	    }
	}

	// @ngInject
	function link$1(luxLinkTemplate, luxLink) {
	    return {
	        template: luxLinkTemplate,
	        restrict: 'A',
	        link: link
	    };

	    function link(scope) {
	        scope.links = luxLink;
	    }
	}

	// @ngInject
	function navbar$1($window, luxNavbarTemplate, luxNavbar) {
	    //
	    return {
	        template: luxNavbarTemplate,
	        restrict: 'E',
	        link: navbar
	    };
	    //
	    function navbar(scope, element, attrs) {
	        scope.navbar = luxNavbar(_.extend({}, scope.navbar, getOptions($window, attrs, 'navbar')));
	        scope.navbar.element = element[0];
	    }
	}

	// @ngInject
	function sidebar$1($window, $compile, $timeout, luxSidebarTemplate, luxSidebar) {
	    //
	    var inner = void 0;

	    return {
	        restrict: 'E',
	        compile: function compile(element) {
	            inner = element.html();

	            element.html('');

	            return {
	                pre: sidebar,
	                post: finalise
	            };
	        }
	    };

	    function sidebar(scope, element, attrs) {
	        var template = void 0;

	        var sidebar = _.extend({}, scope.sidebar, getOptions($window, attrs, 'sidebar')),
	            navbar = _.extend({}, scope.navbar, sidebar.navbar);

	        navbar.top = true;
	        navbar.fluid = true;
	        scope.navbar = navbar;
	        delete scope.sidebar;

	        var sidebars = luxSidebar(sidebar);

	        if (sidebars.length) {
	            scope.sidebars = sidebars;
	            scope.closeSidebars = closeSidebars;
	            //
	            // Add toggle to the navbar
	            _.forEach(sidebars, function (sidebar) {
	                addSidebarToggle(sidebar, scope);
	            });
	            //
	            template = luxSidebarTemplate;
	        } else template = '<lux-navbar></lux-navbar>';

	        element.append($compile(template)(scope));

	        if (inner) {
	            inner = $compile(inner)(scope);

	            if (sidebars.length) querySelector(element, '.sidebar-page').append(inner);else element.after(inner);
	        }

	        function closeSidebars() {
	            _.forEach(sidebars, function (sidebar) {
	                sidebar.close();
	            });
	        }
	    }

	    function finalise(scope, element) {
	        var triggered = false;

	        $timeout(function () {
	            return element.find('nav');
	        }).then(function (nav) {

	            _.element($window).bind('scroll', function () {

	                if ($window.pageYOffset > 150 && triggered === false) {
	                    nav.addClass('navbar--small');
	                    triggered = true;
	                    scope.$apply();
	                } else if ($window.pageYOffset <= 150 && triggered === true) {
	                    nav.removeClass('navbar--small');
	                    triggered = false;
	                    scope.$apply();
	                }
	            });
	        });
	    }
	}

	//
	//  Add toggle functionality to sidebar
	function addSidebarToggle(sidebar, scope) {
	    if (!sidebar.toggleName) return;

	    sidebar.close = function () {
	        setState(false);
	    };

	    function toggle(e) {
	        e.preventDefault();
	        _.forEach(scope.sidebars, function (s) {
	            if (s != sidebar) s.close();
	        });
	        setState(!sidebar.open);
	    }

	    function setState(value) {
	        sidebar.open = value;
	        sidebar.closed = !value;
	        scope.navbar[sidebar.position] = sidebar.open;
	    }

	    var item = {
	        href: sidebar.position,
	        title: sidebar.toggleName,
	        name: sidebar.toggleName,
	        klass: 'sidebar-toggle',
	        icon: 'fa fa-bars',
	        action: toggle,
	        right: 'vert-divider'
	    };

	    if (sidebar.position === 'left') {
	        if (!scope.navbar.itemsLeft) scope.navbar.itemsLeft = [];
	        scope.navbar.itemsLeft.splice(0, 0, item);
	    } else {
	        if (!scope.navbar.itemsRight) scope.navbar.itemsRight = [];
	        scope.navbar.itemsRight.push(item);
	    }
	}

	// lux.nav module
	var luxNavModule = _.module('lux.nav', ['lux']);

	luxNavModule.constant('luxLinkTemplate', linkTemplate);
	luxNavModule.constant('luxNavbarTemplate', navbarTemplate);
	luxNavModule.constant('luxSidebarTemplate', sidebarTemplate);
	luxNavModule.constant('luxNavBarDefaults', navbarDefaults);
	luxNavModule.constant('luxSidebarDefaults', sidebarDefaults);

	luxNavModule.factory('luxLink', link);
	luxNavModule.factory('luxNavbar', navbar);
	luxNavModule.factory('luxSidebar', sidebar);

	luxNavModule.directive('luxLink', link$1);
	luxNavModule.directive('luxNavbar', navbar$1);
	luxNavModule.directive('luxSidebar', sidebar$1);

	/**
	 * Checks if `value` is the
	 * [language type](http://www.ecma-international.org/ecma-262/6.0/#sec-ecmascript-language-types)
	 * of `Object`. (e.g. arrays, functions, objects, regexes, `new Number(0)`, and `new String('')`)
	 *
	 * @static
	 * @memberOf _
	 * @since 0.1.0
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is an object, else `false`.
	 * @example
	 *
	 * _.isObject({});
	 * // => true
	 *
	 * _.isObject([1, 2, 3]);
	 * // => true
	 *
	 * _.isObject(_.noop);
	 * // => true
	 *
	 * _.isObject(null);
	 * // => false
	 */
	function isObject(value) {
	  var type = typeof value === 'undefined' ? 'undefined' : babelHelpers.typeof(value);
	  return !!value && (type == 'object' || type == 'function');
	}

	/**
	 * Gets the timestamp of the number of milliseconds that have elapsed since
	 * the Unix epoch (1 January 1970 00:00:00 UTC).
	 *
	 * @static
	 * @memberOf _
	 * @since 2.4.0
	 * @category Date
	 * @returns {number} Returns the timestamp.
	 * @example
	 *
	 * _.defer(function(stamp) {
	 *   console.log(_.now() - stamp);
	 * }, _.now());
	 * // => Logs the number of milliseconds it took for the deferred invocation.
	 */
	function now() {
	  return Date.now();
	}

	var funcTag = '[object Function]';
	var genTag = '[object GeneratorFunction]';
	/** Used for built-in method references. */
	var objectProto = Object.prototype;

	/**
	 * Used to resolve the
	 * [`toStringTag`](http://ecma-international.org/ecma-262/6.0/#sec-object.prototype.tostring)
	 * of values.
	 */
	var objectToString = objectProto.toString;

	/**
	 * Checks if `value` is classified as a `Function` object.
	 *
	 * @static
	 * @memberOf _
	 * @since 0.1.0
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is correctly classified,
	 *  else `false`.
	 * @example
	 *
	 * _.isFunction(_);
	 * // => true
	 *
	 * _.isFunction(/abc/);
	 * // => false
	 */
	function isFunction(value) {
	  // The use of `Object#toString` avoids issues with the `typeof` operator
	  // in Safari 8 which returns 'object' for typed array and weak map constructors,
	  // and PhantomJS 1.9 which returns 'function' for `NodeList` instances.
	  var tag = isObject(value) ? objectToString.call(value) : '';
	  return tag == funcTag || tag == genTag;
	}

	/**
	 * Checks if `value` is object-like. A value is object-like if it's not `null`
	 * and has a `typeof` result of "object".
	 *
	 * @static
	 * @memberOf _
	 * @since 4.0.0
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is object-like, else `false`.
	 * @example
	 *
	 * _.isObjectLike({});
	 * // => true
	 *
	 * _.isObjectLike([1, 2, 3]);
	 * // => true
	 *
	 * _.isObjectLike(_.noop);
	 * // => false
	 *
	 * _.isObjectLike(null);
	 * // => false
	 */
	function isObjectLike(value) {
	  return !!value && (typeof value === 'undefined' ? 'undefined' : babelHelpers.typeof(value)) == 'object';
	}

	/** `Object#toString` result references. */
	var symbolTag = '[object Symbol]';

	/** Used for built-in method references. */
	var objectProto$1 = Object.prototype;

	/**
	 * Used to resolve the
	 * [`toStringTag`](http://ecma-international.org/ecma-262/6.0/#sec-object.prototype.tostring)
	 * of values.
	 */
	var objectToString$1 = objectProto$1.toString;

	/**
	 * Checks if `value` is classified as a `Symbol` primitive or object.
	 *
	 * @static
	 * @memberOf _
	 * @since 4.0.0
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is correctly classified,
	 *  else `false`.
	 * @example
	 *
	 * _.isSymbol(Symbol.iterator);
	 * // => true
	 *
	 * _.isSymbol('abc');
	 * // => false
	 */
	function isSymbol(value) {
	  return (typeof value === 'undefined' ? 'undefined' : babelHelpers.typeof(value)) == 'symbol' || isObjectLike(value) && objectToString$1.call(value) == symbolTag;
	}

	/** Used as references for various `Number` constants. */
	var NAN = 0 / 0;

	/** Used to match leading and trailing whitespace. */
	var reTrim = /^\s+|\s+$/g;

	/** Used to detect bad signed hexadecimal string values. */
	var reIsBadHex = /^[-+]0x[0-9a-f]+$/i;

	/** Used to detect binary string values. */
	var reIsBinary = /^0b[01]+$/i;

	/** Used to detect octal string values. */
	var reIsOctal = /^0o[0-7]+$/i;

	/** Built-in method references without a dependency on `root`. */
	var freeParseInt = parseInt;

	/**
	 * Converts `value` to a number.
	 *
	 * @static
	 * @memberOf _
	 * @since 4.0.0
	 * @category Lang
	 * @param {*} value The value to process.
	 * @returns {number} Returns the number.
	 * @example
	 *
	 * _.toNumber(3.2);
	 * // => 3.2
	 *
	 * _.toNumber(Number.MIN_VALUE);
	 * // => 5e-324
	 *
	 * _.toNumber(Infinity);
	 * // => Infinity
	 *
	 * _.toNumber('3.2');
	 * // => 3.2
	 */
	function toNumber(value) {
	  if (typeof value == 'number') {
	    return value;
	  }
	  if (isSymbol(value)) {
	    return NAN;
	  }
	  if (isObject(value)) {
	    var other = isFunction(value.valueOf) ? value.valueOf() : value;
	    value = isObject(other) ? other + '' : other;
	  }
	  if (typeof value != 'string') {
	    return value === 0 ? value : +value;
	  }
	  value = value.replace(reTrim, '');
	  var isBinary = reIsBinary.test(value);
	  return isBinary || reIsOctal.test(value) ? freeParseInt(value.slice(2), isBinary ? 2 : 8) : reIsBadHex.test(value) ? NAN : +value;
	}

	/** Used as the `TypeError` message for "Functions" methods. */
	var FUNC_ERROR_TEXT = 'Expected a function';

	/* Built-in method references for those with the same name as other `lodash` methods. */
	var nativeMax = Math.max;
	var nativeMin = Math.min;
	/**
	 * Creates a debounced function that delays invoking `func` until after `wait`
	 * milliseconds have elapsed since the last time the debounced function was
	 * invoked. The debounced function comes with a `cancel` method to cancel
	 * delayed `func` invocations and a `flush` method to immediately invoke them.
	 * Provide an options object to indicate whether `func` should be invoked on
	 * the leading and/or trailing edge of the `wait` timeout. The `func` is invoked
	 * with the last arguments provided to the debounced function. Subsequent calls
	 * to the debounced function return the result of the last `func` invocation.
	 *
	 * **Note:** If `leading` and `trailing` options are `true`, `func` is invoked
	 * on the trailing edge of the timeout only if the debounced function is
	 * invoked more than once during the `wait` timeout.
	 *
	 * See [David Corbacho's article](https://css-tricks.com/debouncing-throttling-explained-examples/)
	 * for details over the differences between `_.debounce` and `_.throttle`.
	 *
	 * @static
	 * @memberOf _
	 * @since 0.1.0
	 * @category Function
	 * @param {Function} func The function to debounce.
	 * @param {number} [wait=0] The number of milliseconds to delay.
	 * @param {Object} [options={}] The options object.
	 * @param {boolean} [options.leading=false]
	 *  Specify invoking on the leading edge of the timeout.
	 * @param {number} [options.maxWait]
	 *  The maximum time `func` is allowed to be delayed before it's invoked.
	 * @param {boolean} [options.trailing=true]
	 *  Specify invoking on the trailing edge of the timeout.
	 * @returns {Function} Returns the new debounced function.
	 * @example
	 *
	 * // Avoid costly calculations while the window size is in flux.
	 * jQuery(window).on('resize', _.debounce(calculateLayout, 150));
	 *
	 * // Invoke `sendMail` when clicked, debouncing subsequent calls.
	 * jQuery(element).on('click', _.debounce(sendMail, 300, {
	 *   'leading': true,
	 *   'trailing': false
	 * }));
	 *
	 * // Ensure `batchLog` is invoked once after 1 second of debounced calls.
	 * var debounced = _.debounce(batchLog, 250, { 'maxWait': 1000 });
	 * var source = new EventSource('/stream');
	 * jQuery(source).on('message', debounced);
	 *
	 * // Cancel the trailing debounced invocation.
	 * jQuery(window).on('popstate', debounced.cancel);
	 */
	function debounce(func, wait, options) {
	  var lastArgs,
	      lastThis,
	      maxWait,
	      result,
	      timerId,
	      lastCallTime,
	      lastInvokeTime = 0,
	      leading = false,
	      maxing = false,
	      trailing = true;

	  if (typeof func != 'function') {
	    throw new TypeError(FUNC_ERROR_TEXT);
	  }
	  wait = toNumber(wait) || 0;
	  if (isObject(options)) {
	    leading = !!options.leading;
	    maxing = 'maxWait' in options;
	    maxWait = maxing ? nativeMax(toNumber(options.maxWait) || 0, wait) : maxWait;
	    trailing = 'trailing' in options ? !!options.trailing : trailing;
	  }

	  function invokeFunc(time) {
	    var args = lastArgs,
	        thisArg = lastThis;

	    lastArgs = lastThis = undefined;
	    lastInvokeTime = time;
	    result = func.apply(thisArg, args);
	    return result;
	  }

	  function leadingEdge(time) {
	    // Reset any `maxWait` timer.
	    lastInvokeTime = time;
	    // Start the timer for the trailing edge.
	    timerId = setTimeout(timerExpired, wait);
	    // Invoke the leading edge.
	    return leading ? invokeFunc(time) : result;
	  }

	  function remainingWait(time) {
	    var timeSinceLastCall = time - lastCallTime,
	        timeSinceLastInvoke = time - lastInvokeTime,
	        result = wait - timeSinceLastCall;

	    return maxing ? nativeMin(result, maxWait - timeSinceLastInvoke) : result;
	  }

	  function shouldInvoke(time) {
	    var timeSinceLastCall = time - lastCallTime,
	        timeSinceLastInvoke = time - lastInvokeTime;

	    // Either this is the first call, activity has stopped and we're at the
	    // trailing edge, the system time has gone backwards and we're treating
	    // it as the trailing edge, or we've hit the `maxWait` limit.
	    return lastCallTime === undefined || timeSinceLastCall >= wait || timeSinceLastCall < 0 || maxing && timeSinceLastInvoke >= maxWait;
	  }

	  function timerExpired() {
	    var time = now();
	    if (shouldInvoke(time)) {
	      return trailingEdge(time);
	    }
	    // Restart the timer.
	    timerId = setTimeout(timerExpired, remainingWait(time));
	  }

	  function trailingEdge(time) {
	    timerId = undefined;

	    // Only invoke if we have `lastArgs` which means `func` has been
	    // debounced at least once.
	    if (trailing && lastArgs) {
	      return invokeFunc(time);
	    }
	    lastArgs = lastThis = undefined;
	    return result;
	  }

	  function cancel() {
	    lastInvokeTime = 0;
	    lastArgs = lastCallTime = lastThis = timerId = undefined;
	  }

	  function flush() {
	    return timerId === undefined ? result : trailingEdge(now());
	  }

	  function debounced() {
	    var time = now(),
	        isInvoking = shouldInvoke(time);

	    lastArgs = arguments;
	    lastThis = this;
	    lastCallTime = time;

	    if (isInvoking) {
	      if (timerId === undefined) {
	        return leadingEdge(lastCallTime);
	      }
	      if (maxing) {
	        // Handle invocations in a tight loop.
	        timerId = setTimeout(timerExpired, wait);
	        return invokeFunc(lastCallTime);
	      }
	    }
	    if (timerId === undefined) {
	      timerId = setTimeout(timerExpired, wait);
	    }
	    return result;
	  }
	  debounced.cancel = cancel;
	  debounced.flush = flush;
	  return debounced;
	}

	/**
	 * The base implementation of `_.findIndex` and `_.findLastIndex` without
	 * support for iteratee shorthands.
	 *
	 * @private
	 * @param {Array} array The array to search.
	 * @param {Function} predicate The function invoked per iteration.
	 * @param {number} fromIndex The index to search from.
	 * @param {boolean} [fromRight] Specify iterating from right to left.
	 * @returns {number} Returns the index of the matched value, else `-1`.
	 */
	function baseFindIndex(array, predicate, fromIndex, fromRight) {
	  var length = array.length,
	      index = fromIndex + (fromRight ? 1 : -1);

	  while (fromRight ? index-- : ++index < length) {
	    if (predicate(array[index], index, array)) {
	      return index;
	    }
	  }
	  return -1;
	}

	/**
	 * Removes all key-value entries from the list cache.
	 *
	 * @private
	 * @name clear
	 * @memberOf ListCache
	 */
	function listCacheClear() {
	  this.__data__ = [];
	}

	/**
	 * Performs a
	 * [`SameValueZero`](http://ecma-international.org/ecma-262/6.0/#sec-samevaluezero)
	 * comparison between two values to determine if they are equivalent.
	 *
	 * @static
	 * @memberOf _
	 * @since 4.0.0
	 * @category Lang
	 * @param {*} value The value to compare.
	 * @param {*} other The other value to compare.
	 * @returns {boolean} Returns `true` if the values are equivalent, else `false`.
	 * @example
	 *
	 * var object = { 'user': 'fred' };
	 * var other = { 'user': 'fred' };
	 *
	 * _.eq(object, object);
	 * // => true
	 *
	 * _.eq(object, other);
	 * // => false
	 *
	 * _.eq('a', 'a');
	 * // => true
	 *
	 * _.eq('a', Object('a'));
	 * // => false
	 *
	 * _.eq(NaN, NaN);
	 * // => true
	 */
	function eq(value, other) {
	  return value === other || value !== value && other !== other;
	}

	/**
	 * Gets the index at which the `key` is found in `array` of key-value pairs.
	 *
	 * @private
	 * @param {Array} array The array to search.
	 * @param {*} key The key to search for.
	 * @returns {number} Returns the index of the matched value, else `-1`.
	 */
	function assocIndexOf(array, key) {
	  var length = array.length;
	  while (length--) {
	    if (eq(array[length][0], key)) {
	      return length;
	    }
	  }
	  return -1;
	}

	/** Used for built-in method references. */
	var arrayProto = Array.prototype;

	/** Built-in value references. */
	var splice = arrayProto.splice;

	/**
	 * Removes `key` and its value from the list cache.
	 *
	 * @private
	 * @name delete
	 * @memberOf ListCache
	 * @param {string} key The key of the value to remove.
	 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
	 */
	function listCacheDelete(key) {
	  var data = this.__data__,
	      index = assocIndexOf(data, key);

	  if (index < 0) {
	    return false;
	  }
	  var lastIndex = data.length - 1;
	  if (index == lastIndex) {
	    data.pop();
	  } else {
	    splice.call(data, index, 1);
	  }
	  return true;
	}

	/**
	 * Gets the list cache value for `key`.
	 *
	 * @private
	 * @name get
	 * @memberOf ListCache
	 * @param {string} key The key of the value to get.
	 * @returns {*} Returns the entry value.
	 */
	function listCacheGet(key) {
	  var data = this.__data__,
	      index = assocIndexOf(data, key);

	  return index < 0 ? undefined : data[index][1];
	}

	/**
	 * Checks if a list cache value for `key` exists.
	 *
	 * @private
	 * @name has
	 * @memberOf ListCache
	 * @param {string} key The key of the entry to check.
	 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
	 */
	function listCacheHas(key) {
	  return assocIndexOf(this.__data__, key) > -1;
	}

	/**
	 * Sets the list cache `key` to `value`.
	 *
	 * @private
	 * @name set
	 * @memberOf ListCache
	 * @param {string} key The key of the value to set.
	 * @param {*} value The value to set.
	 * @returns {Object} Returns the list cache instance.
	 */
	function listCacheSet(key, value) {
	  var data = this.__data__,
	      index = assocIndexOf(data, key);

	  if (index < 0) {
	    data.push([key, value]);
	  } else {
	    data[index][1] = value;
	  }
	  return this;
	}

	/**
	 * Creates an list cache object.
	 *
	 * @private
	 * @constructor
	 * @param {Array} [entries] The key-value pairs to cache.
	 */
	function ListCache(entries) {
	  var index = -1,
	      length = entries ? entries.length : 0;

	  this.clear();
	  while (++index < length) {
	    var entry = entries[index];
	    this.set(entry[0], entry[1]);
	  }
	}

	// Add methods to `ListCache`.
	ListCache.prototype.clear = listCacheClear;
	ListCache.prototype['delete'] = listCacheDelete;
	ListCache.prototype.get = listCacheGet;
	ListCache.prototype.has = listCacheHas;
	ListCache.prototype.set = listCacheSet;

	/**
	 * Removes all key-value entries from the stack.
	 *
	 * @private
	 * @name clear
	 * @memberOf Stack
	 */
	function stackClear() {
	  this.__data__ = new ListCache();
	}

	/**
	 * Removes `key` and its value from the stack.
	 *
	 * @private
	 * @name delete
	 * @memberOf Stack
	 * @param {string} key The key of the value to remove.
	 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
	 */
	function stackDelete(key) {
	  return this.__data__['delete'](key);
	}

	/**
	 * Gets the stack value for `key`.
	 *
	 * @private
	 * @name get
	 * @memberOf Stack
	 * @param {string} key The key of the value to get.
	 * @returns {*} Returns the entry value.
	 */
	function stackGet(key) {
	  return this.__data__.get(key);
	}

	/**
	 * Checks if a stack value for `key` exists.
	 *
	 * @private
	 * @name has
	 * @memberOf Stack
	 * @param {string} key The key of the entry to check.
	 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
	 */
	function stackHas(key) {
	  return this.__data__.has(key);
	}

	/**
	 * Checks if `value` is a host object in IE < 9.
	 *
	 * @private
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is a host object, else `false`.
	 */
	function isHostObject(value) {
	  // Many host objects are `Object` objects that can coerce to strings
	  // despite having improperly defined `toString` methods.
	  var result = false;
	  if (value != null && typeof value.toString != 'function') {
	    try {
	      result = !!(value + '');
	    } catch (e) {}
	  }
	  return result;
	}

	/**
	 * Checks if `value` is a global object.
	 *
	 * @private
	 * @param {*} value The value to check.
	 * @returns {null|Object} Returns `value` if it's a global object, else `null`.
	 */
	function checkGlobal(value) {
	  return value && value.Object === Object ? value : null;
	}

	/** Detect free variable `global` from Node.js. */
	var freeGlobal = checkGlobal((typeof global === 'undefined' ? 'undefined' : babelHelpers.typeof(global)) == 'object' && global);

	/** Detect free variable `self`. */
	var freeSelf = checkGlobal((typeof self === 'undefined' ? 'undefined' : babelHelpers.typeof(self)) == 'object' && self);

	/** Detect `this` as the global object. */
	var thisGlobal = checkGlobal(babelHelpers.typeof(this) == 'object' && this);

	/** Used as a reference to the global object. */
	var root = freeGlobal || freeSelf || thisGlobal || Function('return this')();

	/** Used to detect overreaching core-js shims. */
	var coreJsData = root['__core-js_shared__'];

	/** Used to detect methods masquerading as native. */
	var maskSrcKey = function () {
	  var uid = /[^.]+$/.exec(coreJsData && coreJsData.keys && coreJsData.keys.IE_PROTO || '');
	  return uid ? 'Symbol(src)_1.' + uid : '';
	}();

	/**
	 * Checks if `func` has its source masked.
	 *
	 * @private
	 * @param {Function} func The function to check.
	 * @returns {boolean} Returns `true` if `func` is masked, else `false`.
	 */
	function isMasked(func) {
	  return !!maskSrcKey && maskSrcKey in func;
	}

	/** Used to resolve the decompiled source of functions. */
	var funcToString$1 = Function.prototype.toString;

	/**
	 * Converts `func` to its source code.
	 *
	 * @private
	 * @param {Function} func The function to process.
	 * @returns {string} Returns the source code.
	 */
	function toSource(func) {
	  if (func != null) {
	    try {
	      return funcToString$1.call(func);
	    } catch (e) {}
	    try {
	      return func + '';
	    } catch (e) {}
	  }
	  return '';
	}

	/**
	 * Used to match `RegExp`
	 * [syntax characters](http://ecma-international.org/ecma-262/6.0/#sec-patterns).
	 */
	var reRegExpChar = /[\\^$.*+?()[\]{}|]/g;

	/** Used to detect host constructors (Safari). */
	var reIsHostCtor = /^\[object .+?Constructor\]$/;

	/** Used for built-in method references. */
	var objectProto$2 = Object.prototype;

	/** Used to resolve the decompiled source of functions. */
	var funcToString = Function.prototype.toString;

	/** Used to check objects for own properties. */
	var hasOwnProperty = objectProto$2.hasOwnProperty;

	/** Used to detect if a method is native. */
	var reIsNative = RegExp('^' + funcToString.call(hasOwnProperty).replace(reRegExpChar, '\\$&').replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, '$1.*?') + '$');

	/**
	 * The base implementation of `_.isNative` without bad shim checks.
	 *
	 * @private
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is a native function,
	 *  else `false`.
	 */
	function baseIsNative(value) {
	  if (!isObject(value) || isMasked(value)) {
	    return false;
	  }
	  var pattern = isFunction(value) || isHostObject(value) ? reIsNative : reIsHostCtor;
	  return pattern.test(toSource(value));
	}

	/**
	 * Gets the value at `key` of `object`.
	 *
	 * @private
	 * @param {Object} [object] The object to query.
	 * @param {string} key The key of the property to get.
	 * @returns {*} Returns the property value.
	 */
	function getValue(object, key) {
	  return object == null ? undefined : object[key];
	}

	/**
	 * Gets the native function at `key` of `object`.
	 *
	 * @private
	 * @param {Object} object The object to query.
	 * @param {string} key The key of the method to get.
	 * @returns {*} Returns the function if it's native, else `undefined`.
	 */
	function getNative(object, key) {
	  var value = getValue(object, key);
	  return baseIsNative(value) ? value : undefined;
	}

	/* Built-in method references that are verified to be native. */
	var nativeCreate = getNative(Object, 'create');

	/**
	 * Removes all key-value entries from the hash.
	 *
	 * @private
	 * @name clear
	 * @memberOf Hash
	 */
	function hashClear() {
	  this.__data__ = nativeCreate ? nativeCreate(null) : {};
	}

	/**
	 * Removes `key` and its value from the hash.
	 *
	 * @private
	 * @name delete
	 * @memberOf Hash
	 * @param {Object} hash The hash to modify.
	 * @param {string} key The key of the value to remove.
	 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
	 */
	function hashDelete(key) {
	  return this.has(key) && delete this.__data__[key];
	}

	/** Used to stand-in for `undefined` hash values. */
	var HASH_UNDEFINED = '__lodash_hash_undefined__';

	/** Used for built-in method references. */
	var objectProto$3 = Object.prototype;

	/** Used to check objects for own properties. */
	var hasOwnProperty$1 = objectProto$3.hasOwnProperty;

	/**
	 * Gets the hash value for `key`.
	 *
	 * @private
	 * @name get
	 * @memberOf Hash
	 * @param {string} key The key of the value to get.
	 * @returns {*} Returns the entry value.
	 */
	function hashGet(key) {
	  var data = this.__data__;
	  if (nativeCreate) {
	    var result = data[key];
	    return result === HASH_UNDEFINED ? undefined : result;
	  }
	  return hasOwnProperty$1.call(data, key) ? data[key] : undefined;
	}

	/** Used for built-in method references. */
	var objectProto$4 = Object.prototype;

	/** Used to check objects for own properties. */
	var hasOwnProperty$2 = objectProto$4.hasOwnProperty;

	/**
	 * Checks if a hash value for `key` exists.
	 *
	 * @private
	 * @name has
	 * @memberOf Hash
	 * @param {string} key The key of the entry to check.
	 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
	 */
	function hashHas(key) {
	  var data = this.__data__;
	  return nativeCreate ? data[key] !== undefined : hasOwnProperty$2.call(data, key);
	}

	/** Used to stand-in for `undefined` hash values. */
	var HASH_UNDEFINED$1 = '__lodash_hash_undefined__';

	/**
	 * Sets the hash `key` to `value`.
	 *
	 * @private
	 * @name set
	 * @memberOf Hash
	 * @param {string} key The key of the value to set.
	 * @param {*} value The value to set.
	 * @returns {Object} Returns the hash instance.
	 */
	function hashSet(key, value) {
	  var data = this.__data__;
	  data[key] = nativeCreate && value === undefined ? HASH_UNDEFINED$1 : value;
	  return this;
	}

	/**
	 * Creates a hash object.
	 *
	 * @private
	 * @constructor
	 * @param {Array} [entries] The key-value pairs to cache.
	 */
	function Hash(entries) {
	  var index = -1,
	      length = entries ? entries.length : 0;

	  this.clear();
	  while (++index < length) {
	    var entry = entries[index];
	    this.set(entry[0], entry[1]);
	  }
	}

	// Add methods to `Hash`.
	Hash.prototype.clear = hashClear;
	Hash.prototype['delete'] = hashDelete;
	Hash.prototype.get = hashGet;
	Hash.prototype.has = hashHas;
	Hash.prototype.set = hashSet;

	/* Built-in method references that are verified to be native. */
	var Map$1 = getNative(root, 'Map');

	/**
	 * Removes all key-value entries from the map.
	 *
	 * @private
	 * @name clear
	 * @memberOf MapCache
	 */
	function mapCacheClear() {
	  this.__data__ = {
	    'hash': new Hash(),
	    'map': new (Map$1 || ListCache)(),
	    'string': new Hash()
	  };
	}

	/**
	 * Checks if `value` is suitable for use as unique object key.
	 *
	 * @private
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is suitable, else `false`.
	 */
	function isKeyable(value) {
	  var type = typeof value === 'undefined' ? 'undefined' : babelHelpers.typeof(value);
	  return type == 'string' || type == 'number' || type == 'symbol' || type == 'boolean' ? value !== '__proto__' : value === null;
	}

	/**
	 * Gets the data for `map`.
	 *
	 * @private
	 * @param {Object} map The map to query.
	 * @param {string} key The reference key.
	 * @returns {*} Returns the map data.
	 */
	function getMapData(map, key) {
	  var data = map.__data__;
	  return isKeyable(key) ? data[typeof key == 'string' ? 'string' : 'hash'] : data.map;
	}

	/**
	 * Removes `key` and its value from the map.
	 *
	 * @private
	 * @name delete
	 * @memberOf MapCache
	 * @param {string} key The key of the value to remove.
	 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
	 */
	function mapCacheDelete(key) {
	  return getMapData(this, key)['delete'](key);
	}

	/**
	 * Gets the map value for `key`.
	 *
	 * @private
	 * @name get
	 * @memberOf MapCache
	 * @param {string} key The key of the value to get.
	 * @returns {*} Returns the entry value.
	 */
	function mapCacheGet(key) {
	  return getMapData(this, key).get(key);
	}

	/**
	 * Checks if a map value for `key` exists.
	 *
	 * @private
	 * @name has
	 * @memberOf MapCache
	 * @param {string} key The key of the entry to check.
	 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
	 */
	function mapCacheHas(key) {
	  return getMapData(this, key).has(key);
	}

	/**
	 * Sets the map `key` to `value`.
	 *
	 * @private
	 * @name set
	 * @memberOf MapCache
	 * @param {string} key The key of the value to set.
	 * @param {*} value The value to set.
	 * @returns {Object} Returns the map cache instance.
	 */
	function mapCacheSet(key, value) {
	  getMapData(this, key).set(key, value);
	  return this;
	}

	/**
	 * Creates a map cache object to store key-value pairs.
	 *
	 * @private
	 * @constructor
	 * @param {Array} [entries] The key-value pairs to cache.
	 */
	function MapCache(entries) {
	  var index = -1,
	      length = entries ? entries.length : 0;

	  this.clear();
	  while (++index < length) {
	    var entry = entries[index];
	    this.set(entry[0], entry[1]);
	  }
	}

	// Add methods to `MapCache`.
	MapCache.prototype.clear = mapCacheClear;
	MapCache.prototype['delete'] = mapCacheDelete;
	MapCache.prototype.get = mapCacheGet;
	MapCache.prototype.has = mapCacheHas;
	MapCache.prototype.set = mapCacheSet;

	/** Used as the size to enable large array optimizations. */
	var LARGE_ARRAY_SIZE = 200;

	/**
	 * Sets the stack `key` to `value`.
	 *
	 * @private
	 * @name set
	 * @memberOf Stack
	 * @param {string} key The key of the value to set.
	 * @param {*} value The value to set.
	 * @returns {Object} Returns the stack cache instance.
	 */
	function stackSet(key, value) {
	  var cache = this.__data__;
	  if (cache instanceof ListCache && cache.__data__.length == LARGE_ARRAY_SIZE) {
	    cache = this.__data__ = new MapCache(cache.__data__);
	  }
	  cache.set(key, value);
	  return this;
	}

	/**
	 * Creates a stack cache object to store key-value pairs.
	 *
	 * @private
	 * @constructor
	 * @param {Array} [entries] The key-value pairs to cache.
	 */
	function Stack(entries) {
	  this.__data__ = new ListCache(entries);
	}

	// Add methods to `Stack`.
	Stack.prototype.clear = stackClear;
	Stack.prototype['delete'] = stackDelete;
	Stack.prototype.get = stackGet;
	Stack.prototype.has = stackHas;
	Stack.prototype.set = stackSet;

	/** Used to stand-in for `undefined` hash values. */
	var HASH_UNDEFINED$2 = '__lodash_hash_undefined__';

	/**
	 * Adds `value` to the array cache.
	 *
	 * @private
	 * @name add
	 * @memberOf SetCache
	 * @alias push
	 * @param {*} value The value to cache.
	 * @returns {Object} Returns the cache instance.
	 */
	function setCacheAdd(value) {
	  this.__data__.set(value, HASH_UNDEFINED$2);
	  return this;
	}

	/**
	 * Checks if `value` is in the array cache.
	 *
	 * @private
	 * @name has
	 * @memberOf SetCache
	 * @param {*} value The value to search for.
	 * @returns {number} Returns `true` if `value` is found, else `false`.
	 */
	function setCacheHas(value) {
	  return this.__data__.has(value);
	}

	/**
	 *
	 * Creates an array cache object to store unique values.
	 *
	 * @private
	 * @constructor
	 * @param {Array} [values] The values to cache.
	 */
	function SetCache(values) {
	  var index = -1,
	      length = values ? values.length : 0;

	  this.__data__ = new MapCache();
	  while (++index < length) {
	    this.add(values[index]);
	  }
	}

	// Add methods to `SetCache`.
	SetCache.prototype.add = SetCache.prototype.push = setCacheAdd;
	SetCache.prototype.has = setCacheHas;

	/**
	 * A specialized version of `_.some` for arrays without support for iteratee
	 * shorthands.
	 *
	 * @private
	 * @param {Array} [array] The array to iterate over.
	 * @param {Function} predicate The function invoked per iteration.
	 * @returns {boolean} Returns `true` if any element passes the predicate check,
	 *  else `false`.
	 */
	function arraySome(array, predicate) {
	  var index = -1,
	      length = array ? array.length : 0;

	  while (++index < length) {
	    if (predicate(array[index], index, array)) {
	      return true;
	    }
	  }
	  return false;
	}

	var UNORDERED_COMPARE_FLAG$1 = 1;
	var PARTIAL_COMPARE_FLAG$2 = 2;
	/**
	 * A specialized version of `baseIsEqualDeep` for arrays with support for
	 * partial deep comparisons.
	 *
	 * @private
	 * @param {Array} array The array to compare.
	 * @param {Array} other The other array to compare.
	 * @param {Function} equalFunc The function to determine equivalents of values.
	 * @param {Function} customizer The function to customize comparisons.
	 * @param {number} bitmask The bitmask of comparison flags. See `baseIsEqual`
	 *  for more details.
	 * @param {Object} stack Tracks traversed `array` and `other` objects.
	 * @returns {boolean} Returns `true` if the arrays are equivalent, else `false`.
	 */
	function equalArrays(array, other, equalFunc, customizer, bitmask, stack) {
	  var isPartial = bitmask & PARTIAL_COMPARE_FLAG$2,
	      arrLength = array.length,
	      othLength = other.length;

	  if (arrLength != othLength && !(isPartial && othLength > arrLength)) {
	    return false;
	  }
	  // Assume cyclic values are equal.
	  var stacked = stack.get(array);
	  if (stacked) {
	    return stacked == other;
	  }
	  var index = -1,
	      result = true,
	      seen = bitmask & UNORDERED_COMPARE_FLAG$1 ? new SetCache() : undefined;

	  stack.set(array, other);

	  // Ignore non-index properties.
	  while (++index < arrLength) {
	    var arrValue = array[index],
	        othValue = other[index];

	    if (customizer) {
	      var compared = isPartial ? customizer(othValue, arrValue, index, other, array, stack) : customizer(arrValue, othValue, index, array, other, stack);
	    }
	    if (compared !== undefined) {
	      if (compared) {
	        continue;
	      }
	      result = false;
	      break;
	    }
	    // Recursively compare arrays (susceptible to call stack limits).
	    if (seen) {
	      if (!arraySome(other, function (othValue, othIndex) {
	        if (!seen.has(othIndex) && (arrValue === othValue || equalFunc(arrValue, othValue, customizer, bitmask, stack))) {
	          return seen.add(othIndex);
	        }
	      })) {
	        result = false;
	        break;
	      }
	    } else if (!(arrValue === othValue || equalFunc(arrValue, othValue, customizer, bitmask, stack))) {
	      result = false;
	      break;
	    }
	  }
	  stack['delete'](array);
	  return result;
	}

	/** Built-in value references. */
	var _Symbol = root.Symbol;

	/** Built-in value references. */
	var Uint8Array = root.Uint8Array;

	/**
	 * Converts `map` to its key-value pairs.
	 *
	 * @private
	 * @param {Object} map The map to convert.
	 * @returns {Array} Returns the key-value pairs.
	 */
	function mapToArray(map) {
	  var index = -1,
	      result = Array(map.size);

	  map.forEach(function (value, key) {
	    result[++index] = [key, value];
	  });
	  return result;
	}

	/**
	 * Converts `set` to an array of its values.
	 *
	 * @private
	 * @param {Object} set The set to convert.
	 * @returns {Array} Returns the values.
	 */
	function setToArray(set) {
	  var index = -1,
	      result = Array(set.size);

	  set.forEach(function (value) {
	    result[++index] = value;
	  });
	  return result;
	}

	var UNORDERED_COMPARE_FLAG$2 = 1;
	var PARTIAL_COMPARE_FLAG$3 = 2;
	var boolTag = '[object Boolean]';
	var dateTag = '[object Date]';
	var errorTag = '[object Error]';
	var mapTag = '[object Map]';
	var numberTag = '[object Number]';
	var regexpTag = '[object RegExp]';
	var setTag = '[object Set]';
	var stringTag = '[object String]';
	var symbolTag$1 = '[object Symbol]';
	var arrayBufferTag = '[object ArrayBuffer]';
	var dataViewTag = '[object DataView]';
	var symbolProto = _Symbol ? _Symbol.prototype : undefined;
	var symbolValueOf = symbolProto ? symbolProto.valueOf : undefined;
	/**
	 * A specialized version of `baseIsEqualDeep` for comparing objects of
	 * the same `toStringTag`.
	 *
	 * **Note:** This function only supports comparing values with tags of
	 * `Boolean`, `Date`, `Error`, `Number`, `RegExp`, or `String`.
	 *
	 * @private
	 * @param {Object} object The object to compare.
	 * @param {Object} other The other object to compare.
	 * @param {string} tag The `toStringTag` of the objects to compare.
	 * @param {Function} equalFunc The function to determine equivalents of values.
	 * @param {Function} customizer The function to customize comparisons.
	 * @param {number} bitmask The bitmask of comparison flags. See `baseIsEqual`
	 *  for more details.
	 * @param {Object} stack Tracks traversed `object` and `other` objects.
	 * @returns {boolean} Returns `true` if the objects are equivalent, else `false`.
	 */
	function equalByTag(object, other, tag, equalFunc, customizer, bitmask, stack) {
	  switch (tag) {
	    case dataViewTag:
	      if (object.byteLength != other.byteLength || object.byteOffset != other.byteOffset) {
	        return false;
	      }
	      object = object.buffer;
	      other = other.buffer;

	    case arrayBufferTag:
	      if (object.byteLength != other.byteLength || !equalFunc(new Uint8Array(object), new Uint8Array(other))) {
	        return false;
	      }
	      return true;

	    case boolTag:
	    case dateTag:
	      // Coerce dates and booleans to numbers, dates to milliseconds and
	      // booleans to `1` or `0` treating invalid dates coerced to `NaN` as
	      // not equal.
	      return +object == +other;

	    case errorTag:
	      return object.name == other.name && object.message == other.message;

	    case numberTag:
	      // Treat `NaN` vs. `NaN` as equal.
	      return object != +object ? other != +other : object == +other;

	    case regexpTag:
	    case stringTag:
	      // Coerce regexes to strings and treat strings, primitives and objects,
	      // as equal. See http://www.ecma-international.org/ecma-262/6.0/#sec-regexp.prototype.tostring
	      // for more details.
	      return object == other + '';

	    case mapTag:
	      var convert = mapToArray;

	    case setTag:
	      var isPartial = bitmask & PARTIAL_COMPARE_FLAG$3;
	      convert || (convert = setToArray);

	      if (object.size != other.size && !isPartial) {
	        return false;
	      }
	      // Assume cyclic values are equal.
	      var stacked = stack.get(object);
	      if (stacked) {
	        return stacked == other;
	      }
	      bitmask |= UNORDERED_COMPARE_FLAG$2;
	      stack.set(object, other);

	      // Recursively compare objects (susceptible to call stack limits).
	      return equalArrays(convert(object), convert(other), equalFunc, customizer, bitmask, stack);

	    case symbolTag$1:
	      if (symbolValueOf) {
	        return symbolValueOf.call(object) == symbolValueOf.call(other);
	      }
	  }
	  return false;
	}

	/* Built-in method references for those with the same name as other `lodash` methods. */
	var nativeGetPrototype = Object.getPrototypeOf;

	/**
	 * Gets the `[[Prototype]]` of `value`.
	 *
	 * @private
	 * @param {*} value The value to query.
	 * @returns {null|Object} Returns the `[[Prototype]]`.
	 */
	function getPrototype(value) {
	  return nativeGetPrototype(Object(value));
	}

	/** Used for built-in method references. */
	var objectProto$6 = Object.prototype;

	/** Used to check objects for own properties. */
	var hasOwnProperty$4 = objectProto$6.hasOwnProperty;

	/**
	 * The base implementation of `_.has` without support for deep paths.
	 *
	 * @private
	 * @param {Object} [object] The object to query.
	 * @param {Array|string} key The key to check.
	 * @returns {boolean} Returns `true` if `key` exists, else `false`.
	 */
	function baseHas(object, key) {
	  // Avoid a bug in IE 10-11 where objects with a [[Prototype]] of `null`,
	  // that are composed entirely of index properties, return `false` for
	  // `hasOwnProperty` checks of them.
	  return object != null && (hasOwnProperty$4.call(object, key) || (typeof object === 'undefined' ? 'undefined' : babelHelpers.typeof(object)) == 'object' && key in object && getPrototype(object) === null);
	}

	/* Built-in method references for those with the same name as other `lodash` methods. */
	var nativeKeys = Object.keys;

	/**
	 * The base implementation of `_.keys` which doesn't skip the constructor
	 * property of prototypes or treat sparse arrays as dense.
	 *
	 * @private
	 * @param {Object} object The object to query.
	 * @returns {Array} Returns the array of property names.
	 */
	function baseKeys(object) {
	  return nativeKeys(Object(object));
	}

	/**
	 * The base implementation of `_.times` without support for iteratee shorthands
	 * or max array length checks.
	 *
	 * @private
	 * @param {number} n The number of times to invoke `iteratee`.
	 * @param {Function} iteratee The function invoked per iteration.
	 * @returns {Array} Returns the array of results.
	 */
	function baseTimes(n, iteratee) {
	  var index = -1,
	      result = Array(n);

	  while (++index < n) {
	    result[index] = iteratee(index);
	  }
	  return result;
	}

	/**
	 * The base implementation of `_.property` without support for deep paths.
	 *
	 * @private
	 * @param {string} key The key of the property to get.
	 * @returns {Function} Returns the new accessor function.
	 */
	function baseProperty(key) {
	  return function (object) {
	    return object == null ? undefined : object[key];
	  };
	}

	/**
	 * Gets the "length" property value of `object`.
	 *
	 * **Note:** This function is used to avoid a
	 * [JIT bug](https://bugs.webkit.org/show_bug.cgi?id=142792) that affects
	 * Safari on at least iOS 8.1-8.3 ARM64.
	 *
	 * @private
	 * @param {Object} object The object to query.
	 * @returns {*} Returns the "length" value.
	 */
	var getLength = baseProperty('length');

	/** Used as references for various `Number` constants. */
	var MAX_SAFE_INTEGER = 9007199254740991;

	/**
	 * Checks if `value` is a valid array-like length.
	 *
	 * **Note:** This function is loosely based on
	 * [`ToLength`](http://ecma-international.org/ecma-262/6.0/#sec-tolength).
	 *
	 * @static
	 * @memberOf _
	 * @since 4.0.0
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is a valid length,
	 *  else `false`.
	 * @example
	 *
	 * _.isLength(3);
	 * // => true
	 *
	 * _.isLength(Number.MIN_VALUE);
	 * // => false
	 *
	 * _.isLength(Infinity);
	 * // => false
	 *
	 * _.isLength('3');
	 * // => false
	 */
	function isLength(value) {
	  return typeof value == 'number' && value > -1 && value % 1 == 0 && value <= MAX_SAFE_INTEGER;
	}

	/**
	 * Checks if `value` is array-like. A value is considered array-like if it's
	 * not a function and has a `value.length` that's an integer greater than or
	 * equal to `0` and less than or equal to `Number.MAX_SAFE_INTEGER`.
	 *
	 * @static
	 * @memberOf _
	 * @since 4.0.0
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is array-like, else `false`.
	 * @example
	 *
	 * _.isArrayLike([1, 2, 3]);
	 * // => true
	 *
	 * _.isArrayLike(document.body.children);
	 * // => true
	 *
	 * _.isArrayLike('abc');
	 * // => true
	 *
	 * _.isArrayLike(_.noop);
	 * // => false
	 */
	function isArrayLike(value) {
	  return value != null && isLength(getLength(value)) && !isFunction(value);
	}

	/**
	 * This method is like `_.isArrayLike` except that it also checks if `value`
	 * is an object.
	 *
	 * @static
	 * @memberOf _
	 * @since 4.0.0
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is an array-like object,
	 *  else `false`.
	 * @example
	 *
	 * _.isArrayLikeObject([1, 2, 3]);
	 * // => true
	 *
	 * _.isArrayLikeObject(document.body.children);
	 * // => true
	 *
	 * _.isArrayLikeObject('abc');
	 * // => false
	 *
	 * _.isArrayLikeObject(_.noop);
	 * // => false
	 */
	function isArrayLikeObject(value) {
	  return isObjectLike(value) && isArrayLike(value);
	}

	/** `Object#toString` result references. */
	var argsTag$1 = '[object Arguments]';

	/** Used for built-in method references. */
	var objectProto$7 = Object.prototype;

	/** Used to check objects for own properties. */
	var hasOwnProperty$5 = objectProto$7.hasOwnProperty;

	/**
	 * Used to resolve the
	 * [`toStringTag`](http://ecma-international.org/ecma-262/6.0/#sec-object.prototype.tostring)
	 * of values.
	 */
	var objectToString$2 = objectProto$7.toString;

	/** Built-in value references. */
	var propertyIsEnumerable = objectProto$7.propertyIsEnumerable;

	/**
	 * Checks if `value` is likely an `arguments` object.
	 *
	 * @static
	 * @memberOf _
	 * @since 0.1.0
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is correctly classified,
	 *  else `false`.
	 * @example
	 *
	 * _.isArguments(function() { return arguments; }());
	 * // => true
	 *
	 * _.isArguments([1, 2, 3]);
	 * // => false
	 */
	function isArguments(value) {
	  // Safari 8.1 incorrectly makes `arguments.callee` enumerable in strict mode.
	  return isArrayLikeObject(value) && hasOwnProperty$5.call(value, 'callee') && (!propertyIsEnumerable.call(value, 'callee') || objectToString$2.call(value) == argsTag$1);
	}

	/**
	 * Checks if `value` is classified as an `Array` object.
	 *
	 * @static
	 * @memberOf _
	 * @since 0.1.0
	 * @type {Function}
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is correctly classified,
	 *  else `false`.
	 * @example
	 *
	 * _.isArray([1, 2, 3]);
	 * // => true
	 *
	 * _.isArray(document.body.children);
	 * // => false
	 *
	 * _.isArray('abc');
	 * // => false
	 *
	 * _.isArray(_.noop);
	 * // => false
	 */
	var isArray = Array.isArray;

	/** `Object#toString` result references. */
	var stringTag$1 = '[object String]';

	/** Used for built-in method references. */
	var objectProto$8 = Object.prototype;

	/**
	 * Used to resolve the
	 * [`toStringTag`](http://ecma-international.org/ecma-262/6.0/#sec-object.prototype.tostring)
	 * of values.
	 */
	var objectToString$3 = objectProto$8.toString;

	/**
	 * Checks if `value` is classified as a `String` primitive or object.
	 *
	 * @static
	 * @since 0.1.0
	 * @memberOf _
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is correctly classified,
	 *  else `false`.
	 * @example
	 *
	 * _.isString('abc');
	 * // => true
	 *
	 * _.isString(1);
	 * // => false
	 */
	function isString(value) {
	  return typeof value == 'string' || !isArray(value) && isObjectLike(value) && objectToString$3.call(value) == stringTag$1;
	}

	/**
	 * Creates an array of index keys for `object` values of arrays,
	 * `arguments` objects, and strings, otherwise `null` is returned.
	 *
	 * @private
	 * @param {Object} object The object to query.
	 * @returns {Array|null} Returns index keys, else `null`.
	 */
	function indexKeys(object) {
	  var length = object ? object.length : undefined;
	  if (isLength(length) && (isArray(object) || isString(object) || isArguments(object))) {
	    return baseTimes(length, String);
	  }
	  return null;
	}

	/** Used as references for various `Number` constants. */
	var MAX_SAFE_INTEGER$1 = 9007199254740991;

	/** Used to detect unsigned integer values. */
	var reIsUint = /^(?:0|[1-9]\d*)$/;

	/**
	 * Checks if `value` is a valid array-like index.
	 *
	 * @private
	 * @param {*} value The value to check.
	 * @param {number} [length=MAX_SAFE_INTEGER] The upper bounds of a valid index.
	 * @returns {boolean} Returns `true` if `value` is a valid index, else `false`.
	 */
	function isIndex(value, length) {
	  length = length == null ? MAX_SAFE_INTEGER$1 : length;
	  return !!length && (typeof value == 'number' || reIsUint.test(value)) && value > -1 && value % 1 == 0 && value < length;
	}

	/** Used for built-in method references. */
	var objectProto$9 = Object.prototype;

	/**
	 * Checks if `value` is likely a prototype object.
	 *
	 * @private
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is a prototype, else `false`.
	 */
	function isPrototype(value) {
	  var Ctor = value && value.constructor,
	      proto = typeof Ctor == 'function' && Ctor.prototype || objectProto$9;

	  return value === proto;
	}

	/**
	 * Creates an array of the own enumerable property names of `object`.
	 *
	 * **Note:** Non-object values are coerced to objects. See the
	 * [ES spec](http://ecma-international.org/ecma-262/6.0/#sec-object.keys)
	 * for more details.
	 *
	 * @static
	 * @since 0.1.0
	 * @memberOf _
	 * @category Object
	 * @param {Object} object The object to query.
	 * @returns {Array} Returns the array of property names.
	 * @example
	 *
	 * function Foo() {
	 *   this.a = 1;
	 *   this.b = 2;
	 * }
	 *
	 * Foo.prototype.c = 3;
	 *
	 * _.keys(new Foo);
	 * // => ['a', 'b'] (iteration order is not guaranteed)
	 *
	 * _.keys('hi');
	 * // => ['0', '1']
	 */
	function keys$1(object) {
	  var isProto = isPrototype(object);
	  if (!(isProto || isArrayLike(object))) {
	    return baseKeys(object);
	  }
	  var indexes = indexKeys(object),
	      skipIndexes = !!indexes,
	      result = indexes || [],
	      length = result.length;

	  for (var key in object) {
	    if (baseHas(object, key) && !(skipIndexes && (key == 'length' || isIndex(key, length))) && !(isProto && key == 'constructor')) {
	      result.push(key);
	    }
	  }
	  return result;
	}

	/** Used to compose bitmasks for comparison styles. */
	var PARTIAL_COMPARE_FLAG$4 = 2;

	/**
	 * A specialized version of `baseIsEqualDeep` for objects with support for
	 * partial deep comparisons.
	 *
	 * @private
	 * @param {Object} object The object to compare.
	 * @param {Object} other The other object to compare.
	 * @param {Function} equalFunc The function to determine equivalents of values.
	 * @param {Function} customizer The function to customize comparisons.
	 * @param {number} bitmask The bitmask of comparison flags. See `baseIsEqual`
	 *  for more details.
	 * @param {Object} stack Tracks traversed `object` and `other` objects.
	 * @returns {boolean} Returns `true` if the objects are equivalent, else `false`.
	 */
	function equalObjects(object, other, equalFunc, customizer, bitmask, stack) {
	  var isPartial = bitmask & PARTIAL_COMPARE_FLAG$4,
	      objProps = keys$1(object),
	      objLength = objProps.length,
	      othProps = keys$1(other),
	      othLength = othProps.length;

	  if (objLength != othLength && !isPartial) {
	    return false;
	  }
	  var index = objLength;
	  while (index--) {
	    var key = objProps[index];
	    if (!(isPartial ? key in other : baseHas(other, key))) {
	      return false;
	    }
	  }
	  // Assume cyclic values are equal.
	  var stacked = stack.get(object);
	  if (stacked) {
	    return stacked == other;
	  }
	  var result = true;
	  stack.set(object, other);

	  var skipCtor = isPartial;
	  while (++index < objLength) {
	    key = objProps[index];
	    var objValue = object[key],
	        othValue = other[key];

	    if (customizer) {
	      var compared = isPartial ? customizer(othValue, objValue, key, other, object, stack) : customizer(objValue, othValue, key, object, other, stack);
	    }
	    // Recursively compare objects (susceptible to call stack limits).
	    if (!(compared === undefined ? objValue === othValue || equalFunc(objValue, othValue, customizer, bitmask, stack) : compared)) {
	      result = false;
	      break;
	    }
	    skipCtor || (skipCtor = key == 'constructor');
	  }
	  if (result && !skipCtor) {
	    var objCtor = object.constructor,
	        othCtor = other.constructor;

	    // Non `Object` object instances with different constructors are not equal.
	    if (objCtor != othCtor && 'constructor' in object && 'constructor' in other && !(typeof objCtor == 'function' && objCtor instanceof objCtor && typeof othCtor == 'function' && othCtor instanceof othCtor)) {
	      result = false;
	    }
	  }
	  stack['delete'](object);
	  return result;
	}

	/* Built-in method references that are verified to be native. */
	var DataView = getNative(root, 'DataView');

	/* Built-in method references that are verified to be native. */
	var Promise = getNative(root, 'Promise');

	/* Built-in method references that are verified to be native. */
	var Set$1 = getNative(root, 'Set');

	/* Built-in method references that are verified to be native. */
	var WeakMap = getNative(root, 'WeakMap');

	var mapTag$1 = '[object Map]';
	var objectTag$1 = '[object Object]';
	var promiseTag = '[object Promise]';
	var setTag$1 = '[object Set]';
	var weakMapTag = '[object WeakMap]';
	var dataViewTag$1 = '[object DataView]';

	/** Used for built-in method references. */
	var objectProto$10 = Object.prototype;

	/**
	 * Used to resolve the
	 * [`toStringTag`](http://ecma-international.org/ecma-262/6.0/#sec-object.prototype.tostring)
	 * of values.
	 */
	var objectToString$4 = objectProto$10.toString;

	/** Used to detect maps, sets, and weakmaps. */
	var dataViewCtorString = toSource(DataView);
	var mapCtorString = toSource(Map$1);
	var promiseCtorString = toSource(Promise);
	var setCtorString = toSource(Set$1);
	var weakMapCtorString = toSource(WeakMap);
	/**
	 * Gets the `toStringTag` of `value`.
	 *
	 * @private
	 * @param {*} value The value to query.
	 * @returns {string} Returns the `toStringTag`.
	 */
	function getTag(value) {
	  return objectToString$4.call(value);
	}

	// Fallback for data views, maps, sets, and weak maps in IE 11,
	// for data views in Edge, and promises in Node.js.
	if (DataView && getTag(new DataView(new ArrayBuffer(1))) != dataViewTag$1 || Map$1 && getTag(new Map$1()) != mapTag$1 || Promise && getTag(Promise.resolve()) != promiseTag || Set$1 && getTag(new Set$1()) != setTag$1 || WeakMap && getTag(new WeakMap()) != weakMapTag) {
	  getTag = function getTag(value) {
	    var result = objectToString$4.call(value),
	        Ctor = result == objectTag$1 ? value.constructor : undefined,
	        ctorString = Ctor ? toSource(Ctor) : undefined;

	    if (ctorString) {
	      switch (ctorString) {
	        case dataViewCtorString:
	          return dataViewTag$1;
	        case mapCtorString:
	          return mapTag$1;
	        case promiseCtorString:
	          return promiseTag;
	        case setCtorString:
	          return setTag$1;
	        case weakMapCtorString:
	          return weakMapTag;
	      }
	    }
	    return result;
	  };
	}

	var getTag$1 = getTag;

	var argsTag$2 = '[object Arguments]';
	var arrayTag$1 = '[object Array]';
	var boolTag$1 = '[object Boolean]';
	var dateTag$1 = '[object Date]';
	var errorTag$1 = '[object Error]';
	var funcTag$1 = '[object Function]';
	var mapTag$2 = '[object Map]';
	var numberTag$1 = '[object Number]';
	var objectTag$2 = '[object Object]';
	var regexpTag$1 = '[object RegExp]';
	var setTag$2 = '[object Set]';
	var stringTag$2 = '[object String]';
	var weakMapTag$1 = '[object WeakMap]';
	var arrayBufferTag$1 = '[object ArrayBuffer]';
	var dataViewTag$2 = '[object DataView]';
	var float32Tag = '[object Float32Array]';
	var float64Tag = '[object Float64Array]';
	var int8Tag = '[object Int8Array]';
	var int16Tag = '[object Int16Array]';
	var int32Tag = '[object Int32Array]';
	var uint8Tag = '[object Uint8Array]';
	var uint8ClampedTag = '[object Uint8ClampedArray]';
	var uint16Tag = '[object Uint16Array]';
	var uint32Tag = '[object Uint32Array]';
	/** Used to identify `toStringTag` values of typed arrays. */
	var typedArrayTags = {};
	typedArrayTags[float32Tag] = typedArrayTags[float64Tag] = typedArrayTags[int8Tag] = typedArrayTags[int16Tag] = typedArrayTags[int32Tag] = typedArrayTags[uint8Tag] = typedArrayTags[uint8ClampedTag] = typedArrayTags[uint16Tag] = typedArrayTags[uint32Tag] = true;
	typedArrayTags[argsTag$2] = typedArrayTags[arrayTag$1] = typedArrayTags[arrayBufferTag$1] = typedArrayTags[boolTag$1] = typedArrayTags[dataViewTag$2] = typedArrayTags[dateTag$1] = typedArrayTags[errorTag$1] = typedArrayTags[funcTag$1] = typedArrayTags[mapTag$2] = typedArrayTags[numberTag$1] = typedArrayTags[objectTag$2] = typedArrayTags[regexpTag$1] = typedArrayTags[setTag$2] = typedArrayTags[stringTag$2] = typedArrayTags[weakMapTag$1] = false;

	/** Used for built-in method references. */
	var objectProto$11 = Object.prototype;

	/**
	 * Used to resolve the
	 * [`toStringTag`](http://ecma-international.org/ecma-262/6.0/#sec-object.prototype.tostring)
	 * of values.
	 */
	var objectToString$5 = objectProto$11.toString;

	/**
	 * Checks if `value` is classified as a typed array.
	 *
	 * @static
	 * @memberOf _
	 * @since 3.0.0
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is correctly classified,
	 *  else `false`.
	 * @example
	 *
	 * _.isTypedArray(new Uint8Array);
	 * // => true
	 *
	 * _.isTypedArray([]);
	 * // => false
	 */
	function isTypedArray(value) {
	    return isObjectLike(value) && isLength(value.length) && !!typedArrayTags[objectToString$5.call(value)];
	}

	/** Used to compose bitmasks for comparison styles. */
	var PARTIAL_COMPARE_FLAG$1 = 2;

	/** `Object#toString` result references. */
	var argsTag = '[object Arguments]';
	var arrayTag = '[object Array]';
	var objectTag = '[object Object]';
	/** Used for built-in method references. */
	var objectProto$5 = Object.prototype;

	/** Used to check objects for own properties. */
	var hasOwnProperty$3 = objectProto$5.hasOwnProperty;

	/**
	 * A specialized version of `baseIsEqual` for arrays and objects which performs
	 * deep comparisons and tracks traversed objects enabling objects with circular
	 * references to be compared.
	 *
	 * @private
	 * @param {Object} object The object to compare.
	 * @param {Object} other The other object to compare.
	 * @param {Function} equalFunc The function to determine equivalents of values.
	 * @param {Function} [customizer] The function to customize comparisons.
	 * @param {number} [bitmask] The bitmask of comparison flags. See `baseIsEqual`
	 *  for more details.
	 * @param {Object} [stack] Tracks traversed `object` and `other` objects.
	 * @returns {boolean} Returns `true` if the objects are equivalent, else `false`.
	 */
	function baseIsEqualDeep(object, other, equalFunc, customizer, bitmask, stack) {
	  var objIsArr = isArray(object),
	      othIsArr = isArray(other),
	      objTag = arrayTag,
	      othTag = arrayTag;

	  if (!objIsArr) {
	    objTag = getTag$1(object);
	    objTag = objTag == argsTag ? objectTag : objTag;
	  }
	  if (!othIsArr) {
	    othTag = getTag$1(other);
	    othTag = othTag == argsTag ? objectTag : othTag;
	  }
	  var objIsObj = objTag == objectTag && !isHostObject(object),
	      othIsObj = othTag == objectTag && !isHostObject(other),
	      isSameTag = objTag == othTag;

	  if (isSameTag && !objIsObj) {
	    stack || (stack = new Stack());
	    return objIsArr || isTypedArray(object) ? equalArrays(object, other, equalFunc, customizer, bitmask, stack) : equalByTag(object, other, objTag, equalFunc, customizer, bitmask, stack);
	  }
	  if (!(bitmask & PARTIAL_COMPARE_FLAG$1)) {
	    var objIsWrapped = objIsObj && hasOwnProperty$3.call(object, '__wrapped__'),
	        othIsWrapped = othIsObj && hasOwnProperty$3.call(other, '__wrapped__');

	    if (objIsWrapped || othIsWrapped) {
	      var objUnwrapped = objIsWrapped ? object.value() : object,
	          othUnwrapped = othIsWrapped ? other.value() : other;

	      stack || (stack = new Stack());
	      return equalFunc(objUnwrapped, othUnwrapped, customizer, bitmask, stack);
	    }
	  }
	  if (!isSameTag) {
	    return false;
	  }
	  stack || (stack = new Stack());
	  return equalObjects(object, other, equalFunc, customizer, bitmask, stack);
	}

	/**
	 * The base implementation of `_.isEqual` which supports partial comparisons
	 * and tracks traversed objects.
	 *
	 * @private
	 * @param {*} value The value to compare.
	 * @param {*} other The other value to compare.
	 * @param {Function} [customizer] The function to customize comparisons.
	 * @param {boolean} [bitmask] The bitmask of comparison flags.
	 *  The bitmask may be composed of the following flags:
	 *     1 - Unordered comparison
	 *     2 - Partial comparison
	 * @param {Object} [stack] Tracks traversed `value` and `other` objects.
	 * @returns {boolean} Returns `true` if the values are equivalent, else `false`.
	 */
	function baseIsEqual(value, other, customizer, bitmask, stack) {
	  if (value === other) {
	    return true;
	  }
	  if (value == null || other == null || !isObject(value) && !isObjectLike(other)) {
	    return value !== value && other !== other;
	  }
	  return baseIsEqualDeep(value, other, baseIsEqual, customizer, bitmask, stack);
	}

	var UNORDERED_COMPARE_FLAG = 1;
	var PARTIAL_COMPARE_FLAG = 2;
	/**
	 * The base implementation of `_.isMatch` without support for iteratee shorthands.
	 *
	 * @private
	 * @param {Object} object The object to inspect.
	 * @param {Object} source The object of property values to match.
	 * @param {Array} matchData The property names, values, and compare flags to match.
	 * @param {Function} [customizer] The function to customize comparisons.
	 * @returns {boolean} Returns `true` if `object` is a match, else `false`.
	 */
	function baseIsMatch(object, source, matchData, customizer) {
	  var index = matchData.length,
	      length = index,
	      noCustomizer = !customizer;

	  if (object == null) {
	    return !length;
	  }
	  object = Object(object);
	  while (index--) {
	    var data = matchData[index];
	    if (noCustomizer && data[2] ? data[1] !== object[data[0]] : !(data[0] in object)) {
	      return false;
	    }
	  }
	  while (++index < length) {
	    data = matchData[index];
	    var key = data[0],
	        objValue = object[key],
	        srcValue = data[1];

	    if (noCustomizer && data[2]) {
	      if (objValue === undefined && !(key in object)) {
	        return false;
	      }
	    } else {
	      var stack = new Stack();
	      if (customizer) {
	        var result = customizer(objValue, srcValue, key, object, source, stack);
	      }
	      if (!(result === undefined ? baseIsEqual(srcValue, objValue, customizer, UNORDERED_COMPARE_FLAG | PARTIAL_COMPARE_FLAG, stack) : result)) {
	        return false;
	      }
	    }
	  }
	  return true;
	}

	/**
	 * Checks if `value` is suitable for strict equality comparisons, i.e. `===`.
	 *
	 * @private
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` if suitable for strict
	 *  equality comparisons, else `false`.
	 */
	function isStrictComparable(value) {
	  return value === value && !isObject(value);
	}

	/**
	 * Gets the property names, values, and compare flags of `object`.
	 *
	 * @private
	 * @param {Object} object The object to query.
	 * @returns {Array} Returns the match data of `object`.
	 */
	function getMatchData(object) {
	  var result = keys$1(object),
	      length = result.length;

	  while (length--) {
	    var key = result[length],
	        value = object[key];

	    result[length] = [key, value, isStrictComparable(value)];
	  }
	  return result;
	}

	/**
	 * A specialized version of `matchesProperty` for source values suitable
	 * for strict equality comparisons, i.e. `===`.
	 *
	 * @private
	 * @param {string} key The key of the property to get.
	 * @param {*} srcValue The value to match.
	 * @returns {Function} Returns the new spec function.
	 */
	function matchesStrictComparable(key, srcValue) {
	  return function (object) {
	    if (object == null) {
	      return false;
	    }
	    return object[key] === srcValue && (srcValue !== undefined || key in Object(object));
	  };
	}

	/**
	 * The base implementation of `_.matches` which doesn't clone `source`.
	 *
	 * @private
	 * @param {Object} source The object of property values to match.
	 * @returns {Function} Returns the new spec function.
	 */
	function baseMatches(source) {
	  var matchData = getMatchData(source);
	  if (matchData.length == 1 && matchData[0][2]) {
	    return matchesStrictComparable(matchData[0][0], matchData[0][1]);
	  }
	  return function (object) {
	    return object === source || baseIsMatch(object, source, matchData);
	  };
	}

	/** Used as the `TypeError` message for "Functions" methods. */
	var FUNC_ERROR_TEXT$1 = 'Expected a function';

	/**
	 * Creates a function that memoizes the result of `func`. If `resolver` is
	 * provided, it determines the cache key for storing the result based on the
	 * arguments provided to the memoized function. By default, the first argument
	 * provided to the memoized function is used as the map cache key. The `func`
	 * is invoked with the `this` binding of the memoized function.
	 *
	 * **Note:** The cache is exposed as the `cache` property on the memoized
	 * function. Its creation may be customized by replacing the `_.memoize.Cache`
	 * constructor with one whose instances implement the
	 * [`Map`](http://ecma-international.org/ecma-262/6.0/#sec-properties-of-the-map-prototype-object)
	 * method interface of `delete`, `get`, `has`, and `set`.
	 *
	 * @static
	 * @memberOf _
	 * @since 0.1.0
	 * @category Function
	 * @param {Function} func The function to have its output memoized.
	 * @param {Function} [resolver] The function to resolve the cache key.
	 * @returns {Function} Returns the new memoized function.
	 * @example
	 *
	 * var object = { 'a': 1, 'b': 2 };
	 * var other = { 'c': 3, 'd': 4 };
	 *
	 * var values = _.memoize(_.values);
	 * values(object);
	 * // => [1, 2]
	 *
	 * values(other);
	 * // => [3, 4]
	 *
	 * object.a = 2;
	 * values(object);
	 * // => [1, 2]
	 *
	 * // Modify the result cache.
	 * values.cache.set(object, ['a', 'b']);
	 * values(object);
	 * // => ['a', 'b']
	 *
	 * // Replace `_.memoize.Cache`.
	 * _.memoize.Cache = WeakMap;
	 */
	function memoize(func, resolver) {
	  if (typeof func != 'function' || resolver && typeof resolver != 'function') {
	    throw new TypeError(FUNC_ERROR_TEXT$1);
	  }
	  var memoized = function memoized() {
	    var args = arguments,
	        key = resolver ? resolver.apply(this, args) : args[0],
	        cache = memoized.cache;

	    if (cache.has(key)) {
	      return cache.get(key);
	    }
	    var result = func.apply(this, args);
	    memoized.cache = cache.set(key, result);
	    return result;
	  };
	  memoized.cache = new (memoize.Cache || MapCache)();
	  return memoized;
	}

	// Assign cache to `_.memoize`.
	memoize.Cache = MapCache;

	/** Used as references for various `Number` constants. */
	var INFINITY = 1 / 0;

	/** Used to convert symbols to primitives and strings. */
	var symbolProto$1 = _Symbol ? _Symbol.prototype : undefined;
	var symbolToString = symbolProto$1 ? symbolProto$1.toString : undefined;
	/**
	 * The base implementation of `_.toString` which doesn't convert nullish
	 * values to empty strings.
	 *
	 * @private
	 * @param {*} value The value to process.
	 * @returns {string} Returns the string.
	 */
	function baseToString(value) {
	  // Exit early for strings to avoid a performance hit in some environments.
	  if (typeof value == 'string') {
	    return value;
	  }
	  if (isSymbol(value)) {
	    return symbolToString ? symbolToString.call(value) : '';
	  }
	  var result = value + '';
	  return result == '0' && 1 / value == -INFINITY ? '-0' : result;
	}

	/**
	 * Converts `value` to a string. An empty string is returned for `null`
	 * and `undefined` values. The sign of `-0` is preserved.
	 *
	 * @static
	 * @memberOf _
	 * @since 4.0.0
	 * @category Lang
	 * @param {*} value The value to process.
	 * @returns {string} Returns the string.
	 * @example
	 *
	 * _.toString(null);
	 * // => ''
	 *
	 * _.toString(-0);
	 * // => '-0'
	 *
	 * _.toString([1, 2, 3]);
	 * // => '1,2,3'
	 */
	function toString(value) {
	  return value == null ? '' : baseToString(value);
	}

	/** Used to match property names within property paths. */
	var rePropName = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(\.|\[\])(?:\4|$))/g;

	/** Used to match backslashes in property paths. */
	var reEscapeChar = /\\(\\)?/g;

	/**
	 * Converts `string` to a property path array.
	 *
	 * @private
	 * @param {string} string The string to convert.
	 * @returns {Array} Returns the property path array.
	 */
	var stringToPath = memoize(function (string) {
	  var result = [];
	  toString(string).replace(rePropName, function (match, number, quote, string) {
	    result.push(quote ? string.replace(reEscapeChar, '$1') : number || match);
	  });
	  return result;
	});

	/**
	 * Casts `value` to a path array if it's not one.
	 *
	 * @private
	 * @param {*} value The value to inspect.
	 * @returns {Array} Returns the cast property path array.
	 */
	function castPath(value) {
	  return isArray(value) ? value : stringToPath(value);
	}

	var reIsDeepProp = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/;
	var reIsPlainProp = /^\w*$/;
	/**
	 * Checks if `value` is a property name and not a property path.
	 *
	 * @private
	 * @param {*} value The value to check.
	 * @param {Object} [object] The object to query keys on.
	 * @returns {boolean} Returns `true` if `value` is a property name, else `false`.
	 */
	function isKey(value, object) {
	  if (isArray(value)) {
	    return false;
	  }
	  var type = typeof value === 'undefined' ? 'undefined' : babelHelpers.typeof(value);
	  if (type == 'number' || type == 'symbol' || type == 'boolean' || value == null || isSymbol(value)) {
	    return true;
	  }
	  return reIsPlainProp.test(value) || !reIsDeepProp.test(value) || object != null && value in Object(object);
	}

	/** Used as references for various `Number` constants. */
	var INFINITY$1 = 1 / 0;

	/**
	 * Converts `value` to a string key if it's not a string or symbol.
	 *
	 * @private
	 * @param {*} value The value to inspect.
	 * @returns {string|symbol} Returns the key.
	 */
	function toKey(value) {
	  if (typeof value == 'string' || isSymbol(value)) {
	    return value;
	  }
	  var result = value + '';
	  return result == '0' && 1 / value == -INFINITY$1 ? '-0' : result;
	}

	/**
	 * The base implementation of `_.get` without support for default values.
	 *
	 * @private
	 * @param {Object} object The object to query.
	 * @param {Array|string} path The path of the property to get.
	 * @returns {*} Returns the resolved value.
	 */
	function baseGet(object, path) {
	  path = isKey(path, object) ? [path] : castPath(path);

	  var index = 0,
	      length = path.length;

	  while (object != null && index < length) {
	    object = object[toKey(path[index++])];
	  }
	  return index && index == length ? object : undefined;
	}

	/**
	 * Gets the value at `path` of `object`. If the resolved value is
	 * `undefined`, the `defaultValue` is used in its place.
	 *
	 * @static
	 * @memberOf _
	 * @since 3.7.0
	 * @category Object
	 * @param {Object} object The object to query.
	 * @param {Array|string} path The path of the property to get.
	 * @param {*} [defaultValue] The value returned for `undefined` resolved values.
	 * @returns {*} Returns the resolved value.
	 * @example
	 *
	 * var object = { 'a': [{ 'b': { 'c': 3 } }] };
	 *
	 * _.get(object, 'a[0].b.c');
	 * // => 3
	 *
	 * _.get(object, ['a', '0', 'b', 'c']);
	 * // => 3
	 *
	 * _.get(object, 'a.b.c', 'default');
	 * // => 'default'
	 */
	function get(object, path, defaultValue) {
	  var result = object == null ? undefined : baseGet(object, path);
	  return result === undefined ? defaultValue : result;
	}

	/**
	 * The base implementation of `_.hasIn` without support for deep paths.
	 *
	 * @private
	 * @param {Object} [object] The object to query.
	 * @param {Array|string} key The key to check.
	 * @returns {boolean} Returns `true` if `key` exists, else `false`.
	 */
	function baseHasIn(object, key) {
	  return object != null && key in Object(object);
	}

	/**
	 * Checks if `path` exists on `object`.
	 *
	 * @private
	 * @param {Object} object The object to query.
	 * @param {Array|string} path The path to check.
	 * @param {Function} hasFunc The function to check properties.
	 * @returns {boolean} Returns `true` if `path` exists, else `false`.
	 */
	function hasPath(object, path, hasFunc) {
	  path = isKey(path, object) ? [path] : castPath(path);

	  var result,
	      index = -1,
	      length = path.length;

	  while (++index < length) {
	    var key = toKey(path[index]);
	    if (!(result = object != null && hasFunc(object, key))) {
	      break;
	    }
	    object = object[key];
	  }
	  if (result) {
	    return result;
	  }
	  var length = object ? object.length : 0;
	  return !!length && isLength(length) && isIndex(key, length) && (isArray(object) || isString(object) || isArguments(object));
	}

	/**
	 * Checks if `path` is a direct or inherited property of `object`.
	 *
	 * @static
	 * @memberOf _
	 * @since 4.0.0
	 * @category Object
	 * @param {Object} object The object to query.
	 * @param {Array|string} path The path to check.
	 * @returns {boolean} Returns `true` if `path` exists, else `false`.
	 * @example
	 *
	 * var object = _.create({ 'a': _.create({ 'b': 2 }) });
	 *
	 * _.hasIn(object, 'a');
	 * // => true
	 *
	 * _.hasIn(object, 'a.b');
	 * // => true
	 *
	 * _.hasIn(object, ['a', 'b']);
	 * // => true
	 *
	 * _.hasIn(object, 'b');
	 * // => false
	 */
	function hasIn(object, path) {
	  return object != null && hasPath(object, path, baseHasIn);
	}

	var UNORDERED_COMPARE_FLAG$3 = 1;
	var PARTIAL_COMPARE_FLAG$5 = 2;
	/**
	 * The base implementation of `_.matchesProperty` which doesn't clone `srcValue`.
	 *
	 * @private
	 * @param {string} path The path of the property to get.
	 * @param {*} srcValue The value to match.
	 * @returns {Function} Returns the new spec function.
	 */
	function baseMatchesProperty(path, srcValue) {
	  if (isKey(path) && isStrictComparable(srcValue)) {
	    return matchesStrictComparable(toKey(path), srcValue);
	  }
	  return function (object) {
	    var objValue = get(object, path);
	    return objValue === undefined && objValue === srcValue ? hasIn(object, path) : baseIsEqual(srcValue, objValue, undefined, UNORDERED_COMPARE_FLAG$3 | PARTIAL_COMPARE_FLAG$5);
	  };
	}

	/**
	 * This method returns the first argument given to it.
	 *
	 * @static
	 * @since 0.1.0
	 * @memberOf _
	 * @category Util
	 * @param {*} value Any value.
	 * @returns {*} Returns `value`.
	 * @example
	 *
	 * var object = { 'user': 'fred' };
	 *
	 * console.log(_.identity(object) === object);
	 * // => true
	 */
	function identity(value) {
	  return value;
	}

	/**
	 * A specialized version of `baseProperty` which supports deep paths.
	 *
	 * @private
	 * @param {Array|string} path The path of the property to get.
	 * @returns {Function} Returns the new accessor function.
	 */
	function basePropertyDeep(path) {
	  return function (object) {
	    return baseGet(object, path);
	  };
	}

	/**
	 * Creates a function that returns the value at `path` of a given object.
	 *
	 * @static
	 * @memberOf _
	 * @since 2.4.0
	 * @category Util
	 * @param {Array|string} path The path of the property to get.
	 * @returns {Function} Returns the new accessor function.
	 * @example
	 *
	 * var objects = [
	 *   { 'a': { 'b': 2 } },
	 *   { 'a': { 'b': 1 } }
	 * ];
	 *
	 * _.map(objects, _.property('a.b'));
	 * // => [2, 1]
	 *
	 * _.map(_.sortBy(objects, _.property(['a', 'b'])), 'a.b');
	 * // => [1, 2]
	 */
	function property(path) {
	  return isKey(path) ? baseProperty(toKey(path)) : basePropertyDeep(path);
	}

	/**
	 * The base implementation of `_.iteratee`.
	 *
	 * @private
	 * @param {*} [value=_.identity] The value to convert to an iteratee.
	 * @returns {Function} Returns the iteratee.
	 */
	function baseIteratee(value) {
	  // Don't store the `typeof` result in a variable to avoid a JIT bug in Safari 9.
	  // See https://bugs.webkit.org/show_bug.cgi?id=156034 for more details.
	  if (typeof value == 'function') {
	    return value;
	  }
	  if (value == null) {
	    return identity;
	  }
	  if ((typeof value === 'undefined' ? 'undefined' : babelHelpers.typeof(value)) == 'object') {
	    return isArray(value) ? baseMatchesProperty(value[0], value[1]) : baseMatches(value);
	  }
	  return property(value);
	}

	var INFINITY$2 = 1 / 0;
	var MAX_INTEGER = 1.7976931348623157e+308;
	/**
	 * Converts `value` to a finite number.
	 *
	 * @static
	 * @memberOf _
	 * @since 4.12.0
	 * @category Lang
	 * @param {*} value The value to convert.
	 * @returns {number} Returns the converted number.
	 * @example
	 *
	 * _.toFinite(3.2);
	 * // => 3.2
	 *
	 * _.toFinite(Number.MIN_VALUE);
	 * // => 5e-324
	 *
	 * _.toFinite(Infinity);
	 * // => 1.7976931348623157e+308
	 *
	 * _.toFinite('3.2');
	 * // => 3.2
	 */
	function toFinite(value) {
	  if (!value) {
	    return value === 0 ? value : 0;
	  }
	  value = toNumber(value);
	  if (value === INFINITY$2 || value === -INFINITY$2) {
	    var sign = value < 0 ? -1 : 1;
	    return sign * MAX_INTEGER;
	  }
	  return value === value ? value : 0;
	}

	/**
	 * Converts `value` to an integer.
	 *
	 * **Note:** This method is loosely based on
	 * [`ToInteger`](http://www.ecma-international.org/ecma-262/6.0/#sec-tointeger).
	 *
	 * @static
	 * @memberOf _
	 * @since 4.0.0
	 * @category Lang
	 * @param {*} value The value to convert.
	 * @returns {number} Returns the converted integer.
	 * @example
	 *
	 * _.toInteger(3.2);
	 * // => 3
	 *
	 * _.toInteger(Number.MIN_VALUE);
	 * // => 0
	 *
	 * _.toInteger(Infinity);
	 * // => 1.7976931348623157e+308
	 *
	 * _.toInteger('3.2');
	 * // => 3
	 */
	function toInteger(value) {
	  var result = toFinite(value),
	      remainder = result % 1;

	  return result === result ? remainder ? result - remainder : result : 0;
	}

	/* Built-in method references for those with the same name as other `lodash` methods. */
	var nativeMax$1 = Math.max;

	/**
	 * This method is like `_.find` except that it returns the index of the first
	 * element `predicate` returns truthy for instead of the element itself.
	 *
	 * @static
	 * @memberOf _
	 * @since 1.1.0
	 * @category Array
	 * @param {Array} array The array to search.
	 * @param {Array|Function|Object|string} [predicate=_.identity]
	 *  The function invoked per iteration.
	 * @param {number} [fromIndex=0] The index to search from.
	 * @returns {number} Returns the index of the found element, else `-1`.
	 * @example
	 *
	 * var users = [
	 *   { 'user': 'barney',  'active': false },
	 *   { 'user': 'fred',    'active': false },
	 *   { 'user': 'pebbles', 'active': true }
	 * ];
	 *
	 * _.findIndex(users, function(o) { return o.user == 'barney'; });
	 * // => 0
	 *
	 * // The `_.matches` iteratee shorthand.
	 * _.findIndex(users, { 'user': 'fred', 'active': false });
	 * // => 1
	 *
	 * // The `_.matchesProperty` iteratee shorthand.
	 * _.findIndex(users, ['active', false]);
	 * // => 0
	 *
	 * // The `_.property` iteratee shorthand.
	 * _.findIndex(users, 'active');
	 * // => 2
	 */
	function findIndex(array, predicate, fromIndex) {
	  var length = array ? array.length : 0;
	  if (!length) {
	    return -1;
	  }
	  var index = fromIndex == null ? 0 : toInteger(fromIndex);
	  if (index < 0) {
	    index = nativeMax$1(length + index, 0);
	  }
	  return baseFindIndex(array, baseIteratee(predicate, 3), index);
	}

	/**
	 * A specialized version of `_.forEach` for arrays without support for
	 * iteratee shorthands.
	 *
	 * @private
	 * @param {Array} [array] The array to iterate over.
	 * @param {Function} iteratee The function invoked per iteration.
	 * @returns {Array} Returns `array`.
	 */
	function arrayEach(array, iteratee) {
	  var index = -1,
	      length = array ? array.length : 0;

	  while (++index < length) {
	    if (iteratee(array[index], index, array) === false) {
	      break;
	    }
	  }
	  return array;
	}

	/**
	 * This function is like `assignValue` except that it doesn't assign
	 * `undefined` values.
	 *
	 * @private
	 * @param {Object} object The object to modify.
	 * @param {string} key The key of the property to assign.
	 * @param {*} value The value to assign.
	 */
	function assignMergeValue(object, key, value) {
	  if (value !== undefined && !eq(object[key], value) || typeof key == 'number' && value === undefined && !(key in object)) {
	    object[key] = value;
	  }
	}

	/** Used for built-in method references. */
	var objectProto$12 = Object.prototype;

	/** Used to check objects for own properties. */
	var hasOwnProperty$6 = objectProto$12.hasOwnProperty;

	/**
	 * Assigns `value` to `key` of `object` if the existing value is not equivalent
	 * using [`SameValueZero`](http://ecma-international.org/ecma-262/6.0/#sec-samevaluezero)
	 * for equality comparisons.
	 *
	 * @private
	 * @param {Object} object The object to modify.
	 * @param {string} key The key of the property to assign.
	 * @param {*} value The value to assign.
	 */
	function assignValue(object, key, value) {
	  var objValue = object[key];
	  if (!(hasOwnProperty$6.call(object, key) && eq(objValue, value)) || value === undefined && !(key in object)) {
	    object[key] = value;
	  }
	}

	/**
	 * Copies properties of `source` to `object`.
	 *
	 * @private
	 * @param {Object} source The object to copy properties from.
	 * @param {Array} props The property identifiers to copy.
	 * @param {Object} [object={}] The object to copy properties to.
	 * @param {Function} [customizer] The function to customize copied values.
	 * @returns {Object} Returns `object`.
	 */
	function copyObject(source, props, object, customizer) {
	  object || (object = {});

	  var index = -1,
	      length = props.length;

	  while (++index < length) {
	    var key = props[index];

	    var newValue = customizer ? customizer(object[key], source[key], key, object, source) : source[key];

	    assignValue(object, key, newValue);
	  }
	  return object;
	}

	/**
	 * The base implementation of `_.assign` without support for multiple sources
	 * or `customizer` functions.
	 *
	 * @private
	 * @param {Object} object The destination object.
	 * @param {Object} source The source object.
	 * @returns {Object} Returns `object`.
	 */
	function baseAssign(object, source) {
	  return object && copyObject(source, keys$1(source), object);
	}

	/**
	 * Creates a clone of  `buffer`.
	 *
	 * @private
	 * @param {Buffer} buffer The buffer to clone.
	 * @param {boolean} [isDeep] Specify a deep clone.
	 * @returns {Buffer} Returns the cloned buffer.
	 */
	function cloneBuffer(buffer, isDeep) {
	  if (isDeep) {
	    return buffer.slice();
	  }
	  var result = new buffer.constructor(buffer.length);
	  buffer.copy(result);
	  return result;
	}

	/**
	 * Copies the values of `source` to `array`.
	 *
	 * @private
	 * @param {Array} source The array to copy values from.
	 * @param {Array} [array=[]] The array to copy values to.
	 * @returns {Array} Returns `array`.
	 */
	function copyArray(source, array) {
	  var index = -1,
	      length = source.length;

	  array || (array = Array(length));
	  while (++index < length) {
	    array[index] = source[index];
	  }
	  return array;
	}

	/**
	 * A method that returns a new empty array.
	 *
	 * @static
	 * @memberOf _
	 * @since 4.13.0
	 * @category Util
	 * @returns {Array} Returns the new empty array.
	 * @example
	 *
	 * var arrays = _.times(2, _.stubArray);
	 *
	 * console.log(arrays);
	 * // => [[], []]
	 *
	 * console.log(arrays[0] === arrays[1]);
	 * // => false
	 */
	function stubArray() {
	  return [];
	}

	/** Built-in value references. */
	var getOwnPropertySymbols = Object.getOwnPropertySymbols;

	/**
	 * Creates an array of the own enumerable symbol properties of `object`.
	 *
	 * @private
	 * @param {Object} object The object to query.
	 * @returns {Array} Returns the array of symbols.
	 */
	function getSymbols(object) {
	  // Coerce `object` to an object to avoid non-object errors in V8.
	  // See https://bugs.chromium.org/p/v8/issues/detail?id=3443 for more details.
	  return getOwnPropertySymbols(Object(object));
	}

	// Fallback for IE < 11.
	if (!getOwnPropertySymbols) {
	  getSymbols = stubArray;
	}

	var getSymbols$1 = getSymbols;

	/**
	 * Copies own symbol properties of `source` to `object`.
	 *
	 * @private
	 * @param {Object} source The object to copy symbols from.
	 * @param {Object} [object={}] The object to copy symbols to.
	 * @returns {Object} Returns `object`.
	 */
	function copySymbols(source, object) {
	  return copyObject(source, getSymbols$1(source), object);
	}

	/**
	 * Appends the elements of `values` to `array`.
	 *
	 * @private
	 * @param {Array} array The array to modify.
	 * @param {Array} values The values to append.
	 * @returns {Array} Returns `array`.
	 */
	function arrayPush(array, values) {
	  var index = -1,
	      length = values.length,
	      offset = array.length;

	  while (++index < length) {
	    array[offset + index] = values[index];
	  }
	  return array;
	}

	/**
	 * The base implementation of `getAllKeys` and `getAllKeysIn` which uses
	 * `keysFunc` and `symbolsFunc` to get the enumerable property names and
	 * symbols of `object`.
	 *
	 * @private
	 * @param {Object} object The object to query.
	 * @param {Function} keysFunc The function to get the keys of `object`.
	 * @param {Function} symbolsFunc The function to get the symbols of `object`.
	 * @returns {Array} Returns the array of property names and symbols.
	 */
	function baseGetAllKeys(object, keysFunc, symbolsFunc) {
	  var result = keysFunc(object);
	  return isArray(object) ? result : arrayPush(result, symbolsFunc(object));
	}

	/**
	 * Creates an array of own enumerable property names and symbols of `object`.
	 *
	 * @private
	 * @param {Object} object The object to query.
	 * @returns {Array} Returns the array of property names and symbols.
	 */
	function getAllKeys(object) {
	  return baseGetAllKeys(object, keys$1, getSymbols$1);
	}

	/** Used for built-in method references. */
	var objectProto$13 = Object.prototype;

	/** Used to check objects for own properties. */
	var hasOwnProperty$7 = objectProto$13.hasOwnProperty;

	/**
	 * Initializes an array clone.
	 *
	 * @private
	 * @param {Array} array The array to clone.
	 * @returns {Array} Returns the initialized clone.
	 */
	function initCloneArray(array) {
	  var length = array.length,
	      result = array.constructor(length);

	  // Add properties assigned by `RegExp#exec`.
	  if (length && typeof array[0] == 'string' && hasOwnProperty$7.call(array, 'index')) {
	    result.index = array.index;
	    result.input = array.input;
	  }
	  return result;
	}

	/**
	 * Creates a clone of `arrayBuffer`.
	 *
	 * @private
	 * @param {ArrayBuffer} arrayBuffer The array buffer to clone.
	 * @returns {ArrayBuffer} Returns the cloned array buffer.
	 */
	function cloneArrayBuffer(arrayBuffer) {
	  var result = new arrayBuffer.constructor(arrayBuffer.byteLength);
	  new Uint8Array(result).set(new Uint8Array(arrayBuffer));
	  return result;
	}

	/**
	 * Creates a clone of `dataView`.
	 *
	 * @private
	 * @param {Object} dataView The data view to clone.
	 * @param {boolean} [isDeep] Specify a deep clone.
	 * @returns {Object} Returns the cloned data view.
	 */
	function cloneDataView(dataView, isDeep) {
	  var buffer = isDeep ? cloneArrayBuffer(dataView.buffer) : dataView.buffer;
	  return new dataView.constructor(buffer, dataView.byteOffset, dataView.byteLength);
	}

	/**
	 * Adds the key-value `pair` to `map`.
	 *
	 * @private
	 * @param {Object} map The map to modify.
	 * @param {Array} pair The key-value pair to add.
	 * @returns {Object} Returns `map`.
	 */
	function addMapEntry(map, pair) {
	  // Don't return `Map#set` because it doesn't return the map instance in IE 11.
	  map.set(pair[0], pair[1]);
	  return map;
	}

	/**
	 * A specialized version of `_.reduce` for arrays without support for
	 * iteratee shorthands.
	 *
	 * @private
	 * @param {Array} [array] The array to iterate over.
	 * @param {Function} iteratee The function invoked per iteration.
	 * @param {*} [accumulator] The initial value.
	 * @param {boolean} [initAccum] Specify using the first element of `array` as
	 *  the initial value.
	 * @returns {*} Returns the accumulated value.
	 */
	function arrayReduce(array, iteratee, accumulator, initAccum) {
	  var index = -1,
	      length = array ? array.length : 0;

	  if (initAccum && length) {
	    accumulator = array[++index];
	  }
	  while (++index < length) {
	    accumulator = iteratee(accumulator, array[index], index, array);
	  }
	  return accumulator;
	}

	/**
	 * Creates a clone of `map`.
	 *
	 * @private
	 * @param {Object} map The map to clone.
	 * @param {Function} cloneFunc The function to clone values.
	 * @param {boolean} [isDeep] Specify a deep clone.
	 * @returns {Object} Returns the cloned map.
	 */
	function cloneMap(map, isDeep, cloneFunc) {
	  var array = isDeep ? cloneFunc(mapToArray(map), true) : mapToArray(map);
	  return arrayReduce(array, addMapEntry, new map.constructor());
	}

	/** Used to match `RegExp` flags from their coerced string values. */
	var reFlags = /\w*$/;

	/**
	 * Creates a clone of `regexp`.
	 *
	 * @private
	 * @param {Object} regexp The regexp to clone.
	 * @returns {Object} Returns the cloned regexp.
	 */
	function cloneRegExp(regexp) {
	  var result = new regexp.constructor(regexp.source, reFlags.exec(regexp));
	  result.lastIndex = regexp.lastIndex;
	  return result;
	}

	/**
	 * Adds `value` to `set`.
	 *
	 * @private
	 * @param {Object} set The set to modify.
	 * @param {*} value The value to add.
	 * @returns {Object} Returns `set`.
	 */
	function addSetEntry(set, value) {
	  set.add(value);
	  return set;
	}

	/**
	 * Creates a clone of `set`.
	 *
	 * @private
	 * @param {Object} set The set to clone.
	 * @param {Function} cloneFunc The function to clone values.
	 * @param {boolean} [isDeep] Specify a deep clone.
	 * @returns {Object} Returns the cloned set.
	 */
	function cloneSet(set, isDeep, cloneFunc) {
	  var array = isDeep ? cloneFunc(setToArray(set), true) : setToArray(set);
	  return arrayReduce(array, addSetEntry, new set.constructor());
	}

	var symbolProto$2 = _Symbol ? _Symbol.prototype : undefined;
	var symbolValueOf$1 = symbolProto$2 ? symbolProto$2.valueOf : undefined;
	/**
	 * Creates a clone of the `symbol` object.
	 *
	 * @private
	 * @param {Object} symbol The symbol object to clone.
	 * @returns {Object} Returns the cloned symbol object.
	 */
	function cloneSymbol(symbol) {
	  return symbolValueOf$1 ? Object(symbolValueOf$1.call(symbol)) : {};
	}

	/**
	 * Creates a clone of `typedArray`.
	 *
	 * @private
	 * @param {Object} typedArray The typed array to clone.
	 * @param {boolean} [isDeep] Specify a deep clone.
	 * @returns {Object} Returns the cloned typed array.
	 */
	function cloneTypedArray(typedArray, isDeep) {
	  var buffer = isDeep ? cloneArrayBuffer(typedArray.buffer) : typedArray.buffer;
	  return new typedArray.constructor(buffer, typedArray.byteOffset, typedArray.length);
	}

	var boolTag$3 = '[object Boolean]';
	var dateTag$3 = '[object Date]';
	var mapTag$4 = '[object Map]';
	var numberTag$3 = '[object Number]';
	var regexpTag$3 = '[object RegExp]';
	var setTag$4 = '[object Set]';
	var stringTag$4 = '[object String]';
	var symbolTag$3 = '[object Symbol]';
	var arrayBufferTag$3 = '[object ArrayBuffer]';
	var dataViewTag$4 = '[object DataView]';
	var float32Tag$2 = '[object Float32Array]';
	var float64Tag$2 = '[object Float64Array]';
	var int8Tag$2 = '[object Int8Array]';
	var int16Tag$2 = '[object Int16Array]';
	var int32Tag$2 = '[object Int32Array]';
	var uint8Tag$2 = '[object Uint8Array]';
	var uint8ClampedTag$2 = '[object Uint8ClampedArray]';
	var uint16Tag$2 = '[object Uint16Array]';
	var uint32Tag$2 = '[object Uint32Array]';
	/**
	 * Initializes an object clone based on its `toStringTag`.
	 *
	 * **Note:** This function only supports cloning values with tags of
	 * `Boolean`, `Date`, `Error`, `Number`, `RegExp`, or `String`.
	 *
	 * @private
	 * @param {Object} object The object to clone.
	 * @param {string} tag The `toStringTag` of the object to clone.
	 * @param {Function} cloneFunc The function to clone values.
	 * @param {boolean} [isDeep] Specify a deep clone.
	 * @returns {Object} Returns the initialized clone.
	 */
	function initCloneByTag(object, tag, cloneFunc, isDeep) {
	  var Ctor = object.constructor;
	  switch (tag) {
	    case arrayBufferTag$3:
	      return cloneArrayBuffer(object);

	    case boolTag$3:
	    case dateTag$3:
	      return new Ctor(+object);

	    case dataViewTag$4:
	      return cloneDataView(object, isDeep);

	    case float32Tag$2:case float64Tag$2:
	    case int8Tag$2:case int16Tag$2:case int32Tag$2:
	    case uint8Tag$2:case uint8ClampedTag$2:case uint16Tag$2:case uint32Tag$2:
	      return cloneTypedArray(object, isDeep);

	    case mapTag$4:
	      return cloneMap(object, isDeep, cloneFunc);

	    case numberTag$3:
	    case stringTag$4:
	      return new Ctor(object);

	    case regexpTag$3:
	      return cloneRegExp(object);

	    case setTag$4:
	      return cloneSet(object, isDeep, cloneFunc);

	    case symbolTag$3:
	      return cloneSymbol(object);
	  }
	}

	/** Built-in value references. */
	var objectCreate = Object.create;

	/**
	 * The base implementation of `_.create` without support for assigning
	 * properties to the created object.
	 *
	 * @private
	 * @param {Object} prototype The object to inherit from.
	 * @returns {Object} Returns the new object.
	 */
	function baseCreate(proto) {
	  return isObject(proto) ? objectCreate(proto) : {};
	}

	/**
	 * Initializes an object clone.
	 *
	 * @private
	 * @param {Object} object The object to clone.
	 * @returns {Object} Returns the initialized clone.
	 */
	function initCloneObject(object) {
	  return typeof object.constructor == 'function' && !isPrototype(object) ? baseCreate(getPrototype(object)) : {};
	}

	/**
	 * A method that returns `false`.
	 *
	 * @static
	 * @memberOf _
	 * @since 4.13.0
	 * @category Util
	 * @returns {boolean} Returns `false`.
	 * @example
	 *
	 * _.times(2, _.stubFalse);
	 * // => [false, false]
	 */
	function stubFalse() {
	  return false;
	}

	/** Detect free variable `exports`. */
	var freeExports = (typeof exports === 'undefined' ? 'undefined' : babelHelpers.typeof(exports)) == 'object' && exports;

	/** Detect free variable `module`. */
	var freeModule = freeExports && (typeof module === 'undefined' ? 'undefined' : babelHelpers.typeof(module)) == 'object' && module;

	/** Detect the popular CommonJS extension `module.exports`. */
	var moduleExports = freeModule && freeModule.exports === freeExports;

	/** Built-in value references. */
	var Buffer = moduleExports ? root.Buffer : undefined;

	/**
	 * Checks if `value` is a buffer.
	 *
	 * @static
	 * @memberOf _
	 * @since 4.3.0
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is a buffer, else `false`.
	 * @example
	 *
	 * _.isBuffer(new Buffer(2));
	 * // => true
	 *
	 * _.isBuffer(new Uint8Array(2));
	 * // => false
	 */
	var isBuffer = !Buffer ? stubFalse : function (value) {
	  return value instanceof Buffer;
	};

	var argsTag$3 = '[object Arguments]';
	var arrayTag$2 = '[object Array]';
	var boolTag$2 = '[object Boolean]';
	var dateTag$2 = '[object Date]';
	var errorTag$2 = '[object Error]';
	var funcTag$2 = '[object Function]';
	var genTag$1 = '[object GeneratorFunction]';
	var mapTag$3 = '[object Map]';
	var numberTag$2 = '[object Number]';
	var objectTag$3 = '[object Object]';
	var regexpTag$2 = '[object RegExp]';
	var setTag$3 = '[object Set]';
	var stringTag$3 = '[object String]';
	var symbolTag$2 = '[object Symbol]';
	var weakMapTag$2 = '[object WeakMap]';
	var arrayBufferTag$2 = '[object ArrayBuffer]';
	var dataViewTag$3 = '[object DataView]';
	var float32Tag$1 = '[object Float32Array]';
	var float64Tag$1 = '[object Float64Array]';
	var int8Tag$1 = '[object Int8Array]';
	var int16Tag$1 = '[object Int16Array]';
	var int32Tag$1 = '[object Int32Array]';
	var uint8Tag$1 = '[object Uint8Array]';
	var uint8ClampedTag$1 = '[object Uint8ClampedArray]';
	var uint16Tag$1 = '[object Uint16Array]';
	var uint32Tag$1 = '[object Uint32Array]';
	/** Used to identify `toStringTag` values supported by `_.clone`. */
	var cloneableTags = {};
	cloneableTags[argsTag$3] = cloneableTags[arrayTag$2] = cloneableTags[arrayBufferTag$2] = cloneableTags[dataViewTag$3] = cloneableTags[boolTag$2] = cloneableTags[dateTag$2] = cloneableTags[float32Tag$1] = cloneableTags[float64Tag$1] = cloneableTags[int8Tag$1] = cloneableTags[int16Tag$1] = cloneableTags[int32Tag$1] = cloneableTags[mapTag$3] = cloneableTags[numberTag$2] = cloneableTags[objectTag$3] = cloneableTags[regexpTag$2] = cloneableTags[setTag$3] = cloneableTags[stringTag$3] = cloneableTags[symbolTag$2] = cloneableTags[uint8Tag$1] = cloneableTags[uint8ClampedTag$1] = cloneableTags[uint16Tag$1] = cloneableTags[uint32Tag$1] = true;
	cloneableTags[errorTag$2] = cloneableTags[funcTag$2] = cloneableTags[weakMapTag$2] = false;

	/**
	 * The base implementation of `_.clone` and `_.cloneDeep` which tracks
	 * traversed objects.
	 *
	 * @private
	 * @param {*} value The value to clone.
	 * @param {boolean} [isDeep] Specify a deep clone.
	 * @param {boolean} [isFull] Specify a clone including symbols.
	 * @param {Function} [customizer] The function to customize cloning.
	 * @param {string} [key] The key of `value`.
	 * @param {Object} [object] The parent object of `value`.
	 * @param {Object} [stack] Tracks traversed objects and their clone counterparts.
	 * @returns {*} Returns the cloned value.
	 */
	function baseClone(value, isDeep, isFull, customizer, key, object, stack) {
	  var result;
	  if (customizer) {
	    result = object ? customizer(value, key, object, stack) : customizer(value);
	  }
	  if (result !== undefined) {
	    return result;
	  }
	  if (!isObject(value)) {
	    return value;
	  }
	  var isArr = isArray(value);
	  if (isArr) {
	    result = initCloneArray(value);
	    if (!isDeep) {
	      return copyArray(value, result);
	    }
	  } else {
	    var tag = getTag$1(value),
	        isFunc = tag == funcTag$2 || tag == genTag$1;

	    if (isBuffer(value)) {
	      return cloneBuffer(value, isDeep);
	    }
	    if (tag == objectTag$3 || tag == argsTag$3 || isFunc && !object) {
	      if (isHostObject(value)) {
	        return object ? value : {};
	      }
	      result = initCloneObject(isFunc ? {} : value);
	      if (!isDeep) {
	        return copySymbols(value, baseAssign(result, value));
	      }
	    } else {
	      if (!cloneableTags[tag]) {
	        return object ? value : {};
	      }
	      result = initCloneByTag(value, tag, baseClone, isDeep);
	    }
	  }
	  // Check for circular references and return its corresponding clone.
	  stack || (stack = new Stack());
	  var stacked = stack.get(value);
	  if (stacked) {
	    return stacked;
	  }
	  stack.set(value, result);

	  if (!isArr) {
	    var props = isFull ? getAllKeys(value) : keys$1(value);
	  }
	  // Recursively populate clone (susceptible to call stack limits).
	  arrayEach(props || value, function (subValue, key) {
	    if (props) {
	      key = subValue;
	      subValue = value[key];
	    }
	    assignValue(result, key, baseClone(subValue, isDeep, isFull, customizer, key, value, stack));
	  });
	  return result;
	}

	/** `Object#toString` result references. */
	var objectTag$4 = '[object Object]';

	/** Used for built-in method references. */
	var objectProto$14 = Object.prototype;

	/** Used to resolve the decompiled source of functions. */
	var funcToString$2 = Function.prototype.toString;

	/** Used to check objects for own properties. */
	var hasOwnProperty$8 = objectProto$14.hasOwnProperty;

	/** Used to infer the `Object` constructor. */
	var objectCtorString = funcToString$2.call(Object);

	/**
	 * Used to resolve the
	 * [`toStringTag`](http://ecma-international.org/ecma-262/6.0/#sec-object.prototype.tostring)
	 * of values.
	 */
	var objectToString$6 = objectProto$14.toString;

	/**
	 * Checks if `value` is a plain object, that is, an object created by the
	 * `Object` constructor or one with a `[[Prototype]]` of `null`.
	 *
	 * @static
	 * @memberOf _
	 * @since 0.8.0
	 * @category Lang
	 * @param {*} value The value to check.
	 * @returns {boolean} Returns `true` if `value` is a plain object,
	 *  else `false`.
	 * @example
	 *
	 * function Foo() {
	 *   this.a = 1;
	 * }
	 *
	 * _.isPlainObject(new Foo);
	 * // => false
	 *
	 * _.isPlainObject([1, 2, 3]);
	 * // => false
	 *
	 * _.isPlainObject({ 'x': 0, 'y': 0 });
	 * // => true
	 *
	 * _.isPlainObject(Object.create(null));
	 * // => true
	 */
	function isPlainObject(value) {
	  if (!isObjectLike(value) || objectToString$6.call(value) != objectTag$4 || isHostObject(value)) {
	    return false;
	  }
	  var proto = getPrototype(value);
	  if (proto === null) {
	    return true;
	  }
	  var Ctor = hasOwnProperty$8.call(proto, 'constructor') && proto.constructor;
	  return typeof Ctor == 'function' && Ctor instanceof Ctor && funcToString$2.call(Ctor) == objectCtorString;
	}

	/** Built-in value references. */
	var Reflect = root.Reflect;

	/**
	 * Converts `iterator` to an array.
	 *
	 * @private
	 * @param {Object} iterator The iterator to convert.
	 * @returns {Array} Returns the converted array.
	 */
	function iteratorToArray(iterator) {
	  var data,
	      result = [];

	  while (!(data = iterator.next()).done) {
	    result.push(data.value);
	  }
	  return result;
	}

	/** Used for built-in method references. */
	var objectProto$16 = Object.prototype;

	/** Built-in value references. */
	var enumerate = Reflect ? Reflect.enumerate : undefined;
	var propertyIsEnumerable$1 = objectProto$16.propertyIsEnumerable;
	/**
	 * The base implementation of `_.keysIn` which doesn't skip the constructor
	 * property of prototypes or treat sparse arrays as dense.
	 *
	 * @private
	 * @param {Object} object The object to query.
	 * @returns {Array} Returns the array of property names.
	 */
	function baseKeysIn(object) {
	  object = object == null ? object : Object(object);

	  var result = [];
	  for (var key in object) {
	    result.push(key);
	  }
	  return result;
	}

	// Fallback for IE < 9 with es6-shim.
	if (enumerate && !propertyIsEnumerable$1.call({ 'valueOf': 1 }, 'valueOf')) {
	  baseKeysIn = function baseKeysIn(object) {
	    return iteratorToArray(enumerate(object));
	  };
	}

	var baseKeysIn$1 = baseKeysIn;

	/** Used for built-in method references. */
	var objectProto$15 = Object.prototype;

	/** Used to check objects for own properties. */
	var hasOwnProperty$9 = objectProto$15.hasOwnProperty;

	/**
	 * Creates an array of the own and inherited enumerable property names of `object`.
	 *
	 * **Note:** Non-object values are coerced to objects.
	 *
	 * @static
	 * @memberOf _
	 * @since 3.0.0
	 * @category Object
	 * @param {Object} object The object to query.
	 * @returns {Array} Returns the array of property names.
	 * @example
	 *
	 * function Foo() {
	 *   this.a = 1;
	 *   this.b = 2;
	 * }
	 *
	 * Foo.prototype.c = 3;
	 *
	 * _.keysIn(new Foo);
	 * // => ['a', 'b', 'c'] (iteration order is not guaranteed)
	 */
	function keysIn(object) {
	  var index = -1,
	      isProto = isPrototype(object),
	      props = baseKeysIn$1(object),
	      propsLength = props.length,
	      indexes = indexKeys(object),
	      skipIndexes = !!indexes,
	      result = indexes || [],
	      length = result.length;

	  while (++index < propsLength) {
	    var key = props[index];
	    if (!(skipIndexes && (key == 'length' || isIndex(key, length))) && !(key == 'constructor' && (isProto || !hasOwnProperty$9.call(object, key)))) {
	      result.push(key);
	    }
	  }
	  return result;
	}

	/**
	 * Converts `value` to a plain object flattening inherited enumerable string
	 * keyed properties of `value` to own properties of the plain object.
	 *
	 * @static
	 * @memberOf _
	 * @since 3.0.0
	 * @category Lang
	 * @param {*} value The value to convert.
	 * @returns {Object} Returns the converted plain object.
	 * @example
	 *
	 * function Foo() {
	 *   this.b = 2;
	 * }
	 *
	 * Foo.prototype.c = 3;
	 *
	 * _.assign({ 'a': 1 }, new Foo);
	 * // => { 'a': 1, 'b': 2 }
	 *
	 * _.assign({ 'a': 1 }, _.toPlainObject(new Foo));
	 * // => { 'a': 1, 'b': 2, 'c': 3 }
	 */
	function toPlainObject(value) {
	  return copyObject(value, keysIn(value));
	}

	/**
	 * A specialized version of `baseMerge` for arrays and objects which performs
	 * deep merges and tracks traversed objects enabling objects with circular
	 * references to be merged.
	 *
	 * @private
	 * @param {Object} object The destination object.
	 * @param {Object} source The source object.
	 * @param {string} key The key of the value to merge.
	 * @param {number} srcIndex The index of `source`.
	 * @param {Function} mergeFunc The function to merge values.
	 * @param {Function} [customizer] The function to customize assigned values.
	 * @param {Object} [stack] Tracks traversed source values and their merged
	 *  counterparts.
	 */
	function baseMergeDeep(object, source, key, srcIndex, mergeFunc, customizer, stack) {
	  var objValue = object[key],
	      srcValue = source[key],
	      stacked = stack.get(srcValue);

	  if (stacked) {
	    assignMergeValue(object, key, stacked);
	    return;
	  }
	  var newValue = customizer ? customizer(objValue, srcValue, key + '', object, source, stack) : undefined;

	  var isCommon = newValue === undefined;

	  if (isCommon) {
	    newValue = srcValue;
	    if (isArray(srcValue) || isTypedArray(srcValue)) {
	      if (isArray(objValue)) {
	        newValue = objValue;
	      } else if (isArrayLikeObject(objValue)) {
	        newValue = copyArray(objValue);
	      } else {
	        isCommon = false;
	        newValue = baseClone(srcValue, true);
	      }
	    } else if (isPlainObject(srcValue) || isArguments(srcValue)) {
	      if (isArguments(objValue)) {
	        newValue = toPlainObject(objValue);
	      } else if (!isObject(objValue) || srcIndex && isFunction(objValue)) {
	        isCommon = false;
	        newValue = baseClone(srcValue, true);
	      } else {
	        newValue = objValue;
	      }
	    } else {
	      isCommon = false;
	    }
	  }
	  stack.set(srcValue, newValue);

	  if (isCommon) {
	    // Recursively merge objects and arrays (susceptible to call stack limits).
	    mergeFunc(newValue, srcValue, srcIndex, customizer, stack);
	  }
	  stack['delete'](srcValue);
	  assignMergeValue(object, key, newValue);
	}

	/**
	 * The base implementation of `_.merge` without support for multiple sources.
	 *
	 * @private
	 * @param {Object} object The destination object.
	 * @param {Object} source The source object.
	 * @param {number} srcIndex The index of `source`.
	 * @param {Function} [customizer] The function to customize merged values.
	 * @param {Object} [stack] Tracks traversed source values and their merged
	 *  counterparts.
	 */
	function baseMerge(object, source, srcIndex, customizer, stack) {
	  if (object === source) {
	    return;
	  }
	  if (!(isArray(source) || isTypedArray(source))) {
	    var props = keysIn(source);
	  }
	  arrayEach(props || source, function (srcValue, key) {
	    if (props) {
	      key = srcValue;
	      srcValue = source[key];
	    }
	    if (isObject(srcValue)) {
	      stack || (stack = new Stack());
	      baseMergeDeep(object, source, key, srcIndex, baseMerge, customizer, stack);
	    } else {
	      var newValue = customizer ? customizer(object[key], srcValue, key + '', object, source, stack) : undefined;

	      if (newValue === undefined) {
	        newValue = srcValue;
	      }
	      assignMergeValue(object, key, newValue);
	    }
	  });
	}

	/**
	 * Checks if the given arguments are from an iteratee call.
	 *
	 * @private
	 * @param {*} value The potential iteratee value argument.
	 * @param {*} index The potential iteratee index or key argument.
	 * @param {*} object The potential iteratee object argument.
	 * @returns {boolean} Returns `true` if the arguments are from an iteratee call,
	 *  else `false`.
	 */
	function isIterateeCall(value, index, object) {
	  if (!isObject(object)) {
	    return false;
	  }
	  var type = typeof index === 'undefined' ? 'undefined' : babelHelpers.typeof(index);
	  if (type == 'number' ? isArrayLike(object) && isIndex(index, object.length) : type == 'string' && index in object) {
	    return eq(object[index], value);
	  }
	  return false;
	}

	/**
	 * A faster alternative to `Function#apply`, this function invokes `func`
	 * with the `this` binding of `thisArg` and the arguments of `args`.
	 *
	 * @private
	 * @param {Function} func The function to invoke.
	 * @param {*} thisArg The `this` binding of `func`.
	 * @param {Array} args The arguments to invoke `func` with.
	 * @returns {*} Returns the result of `func`.
	 */
	function apply(func, thisArg, args) {
	  var length = args.length;
	  switch (length) {
	    case 0:
	      return func.call(thisArg);
	    case 1:
	      return func.call(thisArg, args[0]);
	    case 2:
	      return func.call(thisArg, args[0], args[1]);
	    case 3:
	      return func.call(thisArg, args[0], args[1], args[2]);
	  }
	  return func.apply(thisArg, args);
	}

	/** Used as the `TypeError` message for "Functions" methods. */
	var FUNC_ERROR_TEXT$2 = 'Expected a function';

	/* Built-in method references for those with the same name as other `lodash` methods. */
	var nativeMax$2 = Math.max;

	/**
	 * Creates a function that invokes `func` with the `this` binding of the
	 * created function and arguments from `start` and beyond provided as
	 * an array.
	 *
	 * **Note:** This method is based on the
	 * [rest parameter](https://mdn.io/rest_parameters).
	 *
	 * @static
	 * @memberOf _
	 * @since 4.0.0
	 * @category Function
	 * @param {Function} func The function to apply a rest parameter to.
	 * @param {number} [start=func.length-1] The start position of the rest parameter.
	 * @returns {Function} Returns the new function.
	 * @example
	 *
	 * var say = _.rest(function(what, names) {
	 *   return what + ' ' + _.initial(names).join(', ') +
	 *     (_.size(names) > 1 ? ', & ' : '') + _.last(names);
	 * });
	 *
	 * say('hello', 'fred', 'barney', 'pebbles');
	 * // => 'hello fred, barney, & pebbles'
	 */
	function rest(func, start) {
	  if (typeof func != 'function') {
	    throw new TypeError(FUNC_ERROR_TEXT$2);
	  }
	  start = nativeMax$2(start === undefined ? func.length - 1 : toInteger(start), 0);
	  return function () {
	    var args = arguments,
	        index = -1,
	        length = nativeMax$2(args.length - start, 0),
	        array = Array(length);

	    while (++index < length) {
	      array[index] = args[start + index];
	    }
	    switch (start) {
	      case 0:
	        return func.call(this, array);
	      case 1:
	        return func.call(this, args[0], array);
	      case 2:
	        return func.call(this, args[0], args[1], array);
	    }
	    var otherArgs = Array(start + 1);
	    index = -1;
	    while (++index < start) {
	      otherArgs[index] = args[index];
	    }
	    otherArgs[start] = array;
	    return apply(func, this, otherArgs);
	  };
	}

	/**
	 * Creates a function like `_.assign`.
	 *
	 * @private
	 * @param {Function} assigner The function to assign values.
	 * @returns {Function} Returns the new assigner function.
	 */
	function createAssigner(assigner) {
	  return rest(function (object, sources) {
	    var index = -1,
	        length = sources.length,
	        customizer = length > 1 ? sources[length - 1] : undefined,
	        guard = length > 2 ? sources[2] : undefined;

	    customizer = assigner.length > 3 && typeof customizer == 'function' ? (length--, customizer) : undefined;

	    if (guard && isIterateeCall(sources[0], sources[1], guard)) {
	      customizer = length < 3 ? undefined : customizer;
	      length = 1;
	    }
	    object = Object(object);
	    while (++index < length) {
	      var source = sources[index];
	      if (source) {
	        assigner(object, source, index, customizer);
	      }
	    }
	    return object;
	  });
	}

	/**
	 * This method is like `_.assign` except that it recursively merges own and
	 * inherited enumerable string keyed properties of source objects into the
	 * destination object. Source properties that resolve to `undefined` are
	 * skipped if a destination value exists. Array and plain object properties
	 * are merged recursively. Other objects and value types are overridden by
	 * assignment. Source objects are applied from left to right. Subsequent
	 * sources overwrite property assignments of previous sources.
	 *
	 * **Note:** This method mutates `object`.
	 *
	 * @static
	 * @memberOf _
	 * @since 0.5.0
	 * @category Object
	 * @param {Object} object The destination object.
	 * @param {...Object} [sources] The source objects.
	 * @returns {Object} Returns `object`.
	 * @example
	 *
	 * var users = {
	 *   'data': [{ 'user': 'barney' }, { 'user': 'fred' }]
	 * };
	 *
	 * var ages = {
	 *   'data': [{ 'age': 36 }, { 'age': 40 }]
	 * };
	 *
	 * _.merge(users, ages);
	 * // => { 'data': [{ 'user': 'barney', 'age': 36 }, { 'user': 'fred', 'age': 40 }] }
	 */
	var merge = createAssigner(function (object, source, srcIndex) {
	  baseMerge(object, source, srcIndex);
	});

	function parseColumns(grid, metadata) {
	    var permissions = metadata.permissions || {},
	        columnDefs = [],
	        columnHook,
	        column;

	    _.forEach(metadata.columns, function (col) {
	        column = {
	            field: col.name,
	            displayName: col.displayName || col.name,
	            type: getColumnType(col.type),
	            name: col.name
	        };

	        if (col.hidden) column.visible = false;

	        if (!col.sortable) column.enableSorting = false;

	        if (!col.filter) column.enableFiltering = false;

	        columnHook = grid.$provider.columnProcessor(column.type);
	        if (columnHook) columnHook(column, grid);

	        if (_.isString(col.cellFilter)) {
	            column.cellFilter = col.cellFilter;
	        }

	        if (_.isString(col.cellTemplateName)) {
	            column.cellTemplate = grid.wrapCell(col.cellTemplateName);
	        }

	        if (_.isDefined(column.field) && column.field === metadata.repr) {
	            if (permissions.update) {
	                // If there is an update permission then display link
	                var path = grid.options.reprPath || grid.$window.location,
	                    idfield = metadata.id;
	                column.cellTemplate = grid.wrapCell('<a href="' + path + '/{{ row.entity[\'' + idfield + '\'] }}" title="Edit {{ COL_FIELD }}">{{COL_FIELD}}</a>');
	            }
	            // Set repr column as the first column
	            columnDefs.splice(0, 0, column);
	        } else columnDefs.push(column);
	    });

	    return columnDefs;
	}

	function parseData(grid, data) {
	    var result = data.result,
	        options = grid.options;

	    if (!_.isArray(result)) return grid.messages.error('Data grid got bad data from provider');

	    grid.state.total = data.total || result.length;

	    if (data.type !== 'update') options.data = [];

	    _.forEach(result, function (row) {
	        var id = grid.metadata.id;
	        var lookup = {};
	        lookup[id] = row[id];

	        var index = findIndex(options.data, lookup);
	        if (index === -1) {
	            options.data.push(row);
	        } else {
	            options.data[index] = merge(options.data[index], row);
	            flashClass(grid, options.data[index], 'statusUpdated');
	        }
	    });

	    // Update grid height
	    updateGridHeight(grid);
	}

	function stringColumn(column, grid) {
	    column.cellTemplate = grid.wrapCell('{{COL_FIELD}}');
	}

	function urlColumn(column, grid) {
	    column.cellTemplate = grid.wrapCell('<a href="{{COL_FIELD.url || COL_FIELD}}">{{COL_FIELD.repr || COL_FIELD}}</a>');
	}

	function dateColumn(column) {

	    column.sortingAlgorithm = function (a, b) {
	        var dt1 = new Date(a).getTime(),
	            dt2 = new Date(b).getTime();
	        return dt1 === dt2 ? 0 : dt1 < dt2 ? -1 : 1;
	    };
	}

	function booleanColumn(column, grid) {
	    column.cellTemplate = grid.wrapCell('<i ng-class="COL_FIELD ? \'fa fa-check-circle text-success\' : \'fa fa-check-circle text-danger\'"></i>', 'text-center');

	    if (column.enableFiltering) {
	        column.filter = {
	            type: grid.uiGridConstants.filter.SELECT,
	            selectOptions: [{
	                value: 'true',
	                label: 'True'
	            }, { value: 'false', label: 'False' }]
	        };
	    }
	}

	function objectColumn(column, grid) {
	    // TODO: this requires fixing (add a url for example)
	    column.cellTemplate = grid.wrapCell('{{COL_FIELD.repr || COL_FIELD.id || COL_FIELD}}');
	}

	function paginationEvents(grid) {
	    var api = grid.api,
	        scope = grid.$scope,
	        options = grid.options;

	    if (!grid.options.enablePagination) return;

	    api.core.on.sortChanged(scope, debounce(sort, options.requestDelay));
	    api.core.on.filterChanged(scope, debounce(filter, options.requestDelay));
	    api.pagination.on.paginationChanged(scope, debounce(paginate, options.requestDelay));
	}

	// Return column type according to type
	function getColumnType(type) {
	    switch (type) {
	        case 'integer':
	            return 'number';
	        case 'datetime':
	            return 'date';
	        default:
	            return type || 'string';
	    }
	}

	function updateGridHeight(grid) {
	    var state = grid.state,
	        options = grid.options,
	        gridHeight = state.inPage * options.rowHeight + options.offsetGridHeight;

	    if (gridHeight < options.minGridHeight) gridHeight = options.minGridHeight;

	    grid.style = {
	        height: gridHeight + 'px'
	    };
	}

	function sort(grid, sortColumns) {
	    if (sortColumns.length === 0) {
	        grid.state.sortby(undefined);
	        grid.refreshPage();
	    } else {
	        // Build query string for sorting
	        _.forEach(sortColumns, function (column) {
	            grid.state.sortby(column.name + ':' + column.sort.direction);
	        });

	        switch (sortColumns[0].sort.direction) {
	            case grid.uiGridConstants.ASC:
	                grid.refreshPage();
	                break;
	            case grid.uiGridConstants.DESC:
	                grid.refreshPage();
	                break;
	            case undefined:
	                grid.refreshPage();
	                break;
	        }
	    }
	}

	function filter() {
	    var api = this,
	        operator;

	    api.options.gridFilters = {};

	    // Add filters
	    _.forEach(api.columns, function (value) {
	        // Clear data in order to refresh icons
	        if (value.filter.type === 'select') api.options.data = [];

	        if (value.filters[0].term) {
	            if (value.colDef.type === 'string') {
	                operator = 'search';
	            } else {
	                operator = 'eq';
	            }
	            api.options.gridFilters[value.colDef.name + ':' + operator] = value.filters[0].term;
	        }
	    });

	    // Get results
	    api.refreshPage();
	}

	function paginate(pageNumber, pageSize) {
	    var grid = this.lux;

	    grid.state.page = pageNumber;
	    grid.state.limit = pageSize;
	    grid.refresh();
	}

	function flashClass(grid, obj, className) {
	    obj[className] = true;
	    grid.$lux.$timeout(function () {
	        obj[className] = false;
	    }, grid.options.updateTimeout);
	}

	function pop (object, key) {
	    if (object && object[key]) {
	        var value = object[key];
	        delete object[key];
	        return value;
	    }
	}

	// @ngInject
	function menuConfig($luxProvider) {
	    var grid = $luxProvider.grid,
	        defaults = grid.defaults;

	    defaults.enableGridMenu = false;

	    defaults.gridMenu = {
	        'create': {
	            title: 'Add',
	            icon: 'fa fa-plus',
	            permissionType: 'create'
	        },
	        'delete': {
	            title: 'Delete',
	            icon: 'fa fa-trash',
	            permissionType: 'delete',
	            template: deleteTpl
	        },
	        'columnsVisibility': {
	            title: 'Columns visibility',
	            icon: 'fa fa-eye'
	        }
	    };
	}

	function gridMenu (grid) {

	    var $lux = grid.$lux,
	        $uibModal = grid.$injector.get('$uibModal'),
	        scope = grid.$scope.$new(true),
	        stateName = grid.getStateName(),
	        modelName = grid.getModelName(),
	        permissions = grid.options.permissions,
	        actions = {},
	        menu = [],
	        modal;

	    // Add a new model
	    actions.create = function () {
	        grid.$window.location.href += '/add';
	    };

	    // delete one or more selected rows
	    actions.delete = function () {
	        var selected = grid.api.selection.getSelectedRows();

	        if (selected.length) return;

	        var firstField = grid.options.columnDefs[0].field;

	        // Modal settings
	        _.extend(scope, {
	            'stateName': stateName,
	            'repr_field': grid.metaFields.repr || firstField
	            // 'infoMessage': options.modal.delete.messages.info + ' ' + stateName + ':',
	            // 'dangerMessage': options.modal.delete.messages.danger,
	            // 'emptyMessage': options.modal.delete.messages.empty + ' ' + stateName + '.'
	        });

	        // open the modal
	        modal = $uibModal.open({
	            scope: scope,
	            template: grid.options.deleteTpl
	        });

	        modal.result.then(function () {
	            function deleteItem(item) {
	                var defer = $lux.q.defer(),
	                    pk = item[grid.metaFields.id];

	                function onSuccess() {
	                    defer.resolve(grid.options.modal.delete.messages.success);
	                }

	                function onFailure() {
	                    defer.reject(grid.options.modal.delete.messages.error);
	                }

	                grid.dataProvider.deleteItem(pk, onSuccess, onFailure);

	                return defer.promise;
	            }

	            var promises = [];

	            _.forEach(selected, function (item) {
	                promises.push(deleteItem(item));
	            });

	            $lux.q.all(promises).then(function (results) {
	                grid.refreshPage();
	                $lux.messages.success(results[0] + ' ' + results.length + ' ' + stateName);
	            }, function (results) {
	                $lux.messages.error(results + ' ' + stateName);
	            });
	        });
	    };

	    _.forEach(grid.options.gridMenu, function (item, key) {
	        var title = item.title;

	        if (key === 'create') title += ' ' + modelName;

	        var menuItem = {
	            title: title,
	            icon: item.icon,
	            action: actions[key]
	        };

	        // If there is an permission to element then shows this item in menu
	        if (item.permissionType) {
	            if (permissions[item.permissionType]) menu.push(menuItem);
	        } else menu.push(menuItem);
	    });

	    grid.options.gridMenuCustomItems = menu;
	}

	var deleteTpl = '<div class="modal-header">\n    <button type="button" class="close" aria-label="Close" ng-click="$dismiss()"><span aria-hidden="true">&times;</span></button>\n    <h4 class="modal-title"><i class="fa fa-trash"></i> Delete {{stateName}}</h4>\n</div>\n<div class="modal-body">\n    <p class="modal-info">{{infoMessage}}</p>\n    <ul class="modal-items">\n        <li ng-repeat="item in selected">{{item[repr_field]}}</li>\n    </ul>\n    <p class="text-danger cannot-undo">{{dangerMessage}}</p>\n</div>\n<div class="modal-footer">\n    <button type="button" class="btn btn-primary" ng-click="$close()">Yes</button>\n    <button type="button" class="btn btn-default" ng-click="$dismiss()">No</button>\n</div>';

	var cellClass = 'ui-grid-cell-contents';

	var Grid = function (_LuxComponent) {
	    babelHelpers.inherits(Grid, _LuxComponent);

	    function Grid($lux, provider, options) {
	        babelHelpers.classCallCheck(this, Grid);

	        var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(Grid).call(this, $lux));

	        _this.$provider = provider;
	        _this.options = options;
	        _this.state = new State(_this);
	        return _this;
	    }

	    babelHelpers.createClass(Grid, [{
	        key: 'refresh',
	        value: function refresh() {
	            this.$dataProvider.getPage();
	        }
	    }, {
	        key: 'wrapCell',
	        value: function wrapCell(cell, klass) {
	            var cl = cellClass;
	            if (klass) cl = cl + ' ' + klass;
	            return '<div class="' + cl + '">' + cell + '</div>';
	        }
	    }, {
	        key: '$onLoaded',
	        value: function $onLoaded(directives) {
	            this.$directives = directives;
	            this.$dataProvider = this.$provider.dataProvider(this.options.dataProvider)(this);
	            build(this);
	        }
	    }, {
	        key: '$onLink',
	        value: function $onLink(scope, element) {
	            this.$scope = scope;
	            this.$element = element;
	            build(this);
	        }
	    }, {
	        key: '$onMetadata',
	        value: function $onMetadata(metadata) {
	            var options = this.options;

	            if (metadata) {
	                if (metadata['default-limit']) options.paginationPageSize = pop(metadata, 'default-limit');
	                this.metadata = metadata;
	                options.columnDefs = parseColumns(this, metadata);
	            }

	            if (options.enableGridMenu) gridMenu(this);

	            this.$element.replaceWith(this.$compile(gridTpl(this))(this.$scope));
	        }
	    }, {
	        key: '$onRegisterApi',
	        value: function $onRegisterApi(api) {
	            this.options = api.grid.options;
	            this.api = api;
	            api.lux = this;
	            this.$provider.onInit(this);
	            this.$dataProvider.getPage();
	        }
	    }, {
	        key: '$onData',
	        value: function $onData(data) {
	            parseData(this, data);
	        }
	    }, {
	        key: 'uiGridConstants',
	        get: function get() {
	            return this.$injector.get('uiGridConstants');
	        }
	    }]);
	    return Grid;
	}(LuxComponent);

	var State = function () {
	    function State(grid) {
	        babelHelpers.classCallCheck(this, State);

	        this.$grid = grid;
	    }

	    babelHelpers.createClass(State, [{
	        key: 'options',
	        get: function get() {
	            return this.$grid.options;
	        }
	    }, {
	        key: 'page',
	        get: function get() {
	            return this.$grid.options.paginationCurrentPage;
	        },
	        set: function set(value) {
	            this.$grid.options.paginationCurrentPage = value;
	        }
	    }, {
	        key: 'limit',
	        get: function get() {
	            return this.$grid.options.paginationPageSize;
	        },
	        set: function set(value) {
	            this.$grid.options.paginationPageSize = value;
	        }
	    }, {
	        key: 'total',
	        get: function get() {
	            return this.$grid.options.totalItems;
	        },
	        set: function set(value) {
	            this.$grid.options.totalItems = value;
	        }
	    }, {
	        key: 'totalPages',
	        get: function get() {
	            return this.$grid.api.pagination.getTotalPages();
	        }
	    }, {
	        key: 'offset',
	        get: function get() {
	            return this.limit * (this.page - 1);
	        }
	    }, {
	        key: 'inPage',
	        get: function get() {
	            return Math.min(this.total - this.offset, this.limit);
	        }
	    }, {
	        key: 'query',
	        get: function get() {
	            // Add filter if available
	            var params = {
	                page: this.page,
	                limit: this.limit,
	                offset: this.offset,
	                sortby: this.sortby
	            };

	            if (this.options.gridFilters) _.extend(params, this.options.gridFilters);

	            return params;
	        }
	    }]);
	    return State;
	}();

	function build(grid) {
	    if (grid.$element && grid.$dataProvider) {
	        var onRegisterApi = grid.options.onRegisterApi;

	        grid.options.onRegisterApi = function (api) {
	            grid.$onRegisterApi(api);
	            if (onRegisterApi) onRegisterApi(api);
	        };
	        grid.$dataProvider.connect();
	    }
	}

	function gridTpl(grid) {
	    return '<div class=\'grid\'\nui-grid=\'grid.options\'\nng-style="grid.style"\n' + grid.$directives + '>\n</div>';
	}

	// @ngInject
	function luxGrid ($luxProvider) {

	    var providerMap = {},
	        onInitCallbacks = [],
	        columnProcessors = {},
	        defaults = {
	        //
	        // Auto Resize
	        enableAutoResize: true,
	        //
	        // Filtering
	        enableFiltering: true,
	        useExternalFiltering: true,
	        gridFilters: {},
	        //
	        // Sorting
	        useExternalSorting: true,
	        //
	        // Scrollbar display: 0 - never, 1 - always, 2 - when needed
	        enableHorizontalScrollbar: 0,
	        enableVerticalScrollbar: 0,
	        //
	        rowHeight: 30,
	        minGridHeight: 250,
	        offsetGridHeight: 102,
	        //
	        // Grid pagination
	        enablePagination: true,
	        useExternalPagination: true,
	        paginationPageSizes: [25, 50, 100, 250],
	        paginationPageSize: 25,
	        //
	        gridMenuShowHideColumns: false,
	        //
	        // Column resizing
	        enableResizeColumn: true,
	        //
	        // Row Selection
	        enableSelect: true,
	        multiSelect: true,
	        // enableRowHeaderSelection: false,
	        //
	        // Lux specific options
	        // request delay in ms
	        requestDelay: 100,
	        updateTimeout: 2000
	    };
	    var defaultProvider = void 0;

	    $luxProvider.grid = _.extend(grid, {
	        defaults: defaults,
	        // get/set data Provider
	        dataProvider: dataProvider,
	        // processor for columns
	        columnProcessor: columnProcessor,
	        // callback when the grid initialise
	        onInit: onInit
	    });

	    $luxProvider.plugins.grid = $luxProvider.grid;

	    function dataProvider(type, dataProvider) {
	        if (arguments.length === 2) {
	            providerMap[type] = dataProvider;
	            if (!defaultProvider) defaultProvider = type;
	            return this;
	        } else {
	            if (!type) type = defaultProvider;
	            var provider = providerMap[type];
	            if (provider) return provider;
	            throw Error('No data provider found');
	        }
	    }

	    function onInit(grid) {
	        if (grid instanceof Grid) {
	            _.forEach(onInitCallbacks, function (callback) {
	                callback(grid);
	            });
	        } else {
	            onInitCallbacks.push(grid);
	            return this;
	        }
	    }

	    function columnProcessor(type, hook) {
	        if (arguments.length === 1) return columnProcessors[type];else {
	            columnProcessors[type] = hook;
	            return this;
	        }
	    }

	    // Grid constructor
	    function grid(options) {
	        var $lux = this,
	            provider = $luxProvider.grid;

	        options = reversemerge(options || {}, provider.defaults);
	        var modules = ['ui.grid'],
	            directives = [];

	        if (options.enableSelect) {
	            directives.push('ui-grid-selection');
	            modules.push('ui.grid.selection');
	        }

	        if (options.enablePagination) {
	            directives.push('ui-grid-pagination');
	            modules.push('ui.grid.pagination');
	        }
	        //
	        //  Grid auto resize
	        if (options.enableAutoResize) {
	            directives.push('ui-grid-auto-resize');
	            modules.push('ui.grid.autoResize');
	        }
	        //
	        // Column resizing
	        if (options.enableResizeColumn) {
	            modules.push('ui.grid.resizeColumns');
	            directives.push('ui-grid-resize-columns');
	        }

	        var grid = new Grid($lux, provider, options);

	        $lux.require(['angular-ui-grid', 'angular-ui-bootstrap'], modules, function () {
	            grid.$onLoaded(directives.join(' '));
	        });

	        return grid;
	    }
	}

	function luxGridDirective () {

	    GridController.$inject = ["$scope", "$lux"];
	    return {
	        restrict: 'AE',
	        scope: {
	            gridOptions: '=?'
	        },
	        controller: GridController,
	        link: link
	    };

	    // @ngInject
	    function GridController($scope, $lux) {
	        $scope.grid = $lux.grid($scope.gridOptions);
	    }

	    function link($scope, element) {
	        $scope.grid.$onLink($scope, element);
	    }
	}

	var Rest = function () {
	    function Rest(grid) {
	        babelHelpers.classCallCheck(this, Rest);

	        this.grid = grid;
	        this.api = grid.$lux.api(grid.options.target);
	    }

	    babelHelpers.createClass(Rest, [{
	        key: 'connect',
	        value: function connect() {
	            return this.getMetadata();
	        }
	    }, {
	        key: 'getMetadata',
	        value: function getMetadata() {
	            var grid = this.grid;
	            this.api.get({
	                path: 'metadata'
	            }).success(function (metadata) {
	                grid.$onMetadata(metadata);
	            });
	        }
	    }, {
	        key: 'getData',
	        value: function getData(options) {
	            var grid = this.grid,
	                query = grid.state.query;

	            _.extend(query, options);

	            return this.api.get({ params: query }).success(function (data) {
	                grid.$onData(data);
	            });
	        }
	    }, {
	        key: 'getPage',
	        value: function getPage(options) {
	            return this.getData(options);
	        }
	    }, {
	        key: 'deleteItem',
	        value: function deleteItem(identifier) {
	            return this.api.delete({ path: this._subPath + '/' + identifier });
	        }
	    }]);
	    return Rest;
	}();

	function rest$1(grid) {
	    return new Rest(grid);
	}

	rest$1.prototype = Rest.prototype;

	// @ngInject
	function registerProviders ($luxProvider) {
	    var grid = $luxProvider.grid;

	    grid.dataProvider('rest', rest$1).columnProcessor('date', dateColumn).columnProcessor('datetime', dateColumn).columnProcessor('boolean', booleanColumn).columnProcessor('string', stringColumn).columnProcessor('url', urlColumn).columnProcessor('object', objectColumn).onInit(paginationEvents);
	}

	// lux.nav module
	var luxGridModule = _.module('lux.grid', ['lux']);

	luxGridModule.config(luxGrid);

	luxGridModule.directive('luxGrid', luxGridDirective);

	luxGridModule.config(registerProviders);

	luxGridModule.config(menuConfig);

	var version$1 = "0.7.0";

	function s4 () {
	    return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
	}

	exports.version = version$1;
	exports.querySelector = querySelector;
	exports.s4 = s4;
	exports.noop = noop;
	exports.urlBase64Decode = urlBase64Decode;
	exports.getOptions = getOptions;
	exports.jsLib = jsLib;
	exports.urlResolve = urlResolve;
	exports.urlIsSameOrigin = urlIsSameOrigin;
	exports.urlIsAbsolute = urlIsAbsolute;
	exports.urlJoin = urlJoin;

}((this.lux = this.lux || {})));
define("../../build/lux", function(){});

require([
    'require.config',
    'angular',
    '../../build/lux'
], function(lux, angular) {
    'use strict';

    angular.bootstrap('website', ['lux.form', 'lux.cms', 'lux.nav']);
});

define("app", function(){});

