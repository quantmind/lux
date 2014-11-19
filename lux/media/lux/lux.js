//      Lux Library - v0.1.0

//      Compiled 2014-11-19.
//      Copyright (c) 2014 - Luca Sbardella
//      Licensed BSD.
//      For all details and documentation:
//      http://quantmind.github.io/lux
//
(function (factory) {
    var root = this;
    if (typeof module === "object" && module.exports)
        root = module.exports;
    //
    if (typeof define === 'function' && define.amd) {
        // Support AMD. Register as an anonymous module.
        // NOTE: List all dependencies in AMD style
        var deps = ['angular'];
        if (typeof rcfg === 'object')
            deps = rcfg.min(deps);
        define(deps, function (angular) {
            root.lux = factory(angular, root);
            return root.lux;
        });
    } else {
        // No AMD. Set module as a global variable
        // NOTE: Pass dependencies to factory function
        // (assume that angular is also global.)
        root.lux = factory(angular, root);
    }
}(
function(angular, root) {
    "use strict";

    var lux = root.lux || {};
    lux.version = '0.1.0';

    var forEach = angular.forEach,
        extend = angular.extend,
        angular_bootstrapped = false,
        isArray = angular.isArray,
        isString = angular.isString,
        $ = angular.element,
        slice = Array.prototype.slice,
        lazyApplications = {},
        defaults = {
            url: '',    // base url for the web site
            media: '',  // default url for media content
            html5mode: true, //  html5mode for angular
            hashPrefix: '!',
            ngModules: [],
            loadRequire: function (callback) {
                callback();
            }
        };
    //
    lux.$ = $;
    lux.angular = angular;
    lux.forEach = angular.forEach;
    lux.context = extend({}, defaults, lux.context);

    // Extend lux context with additional data
    lux.extend = function (context) {
        lux.context = extend(lux.context, context);
        return lux;
    };

    lux.media = function (url, ctx) {
        if (!ctx)
            ctx = lux.context;
        return joinUrl(ctx.url, ctx.media, url);
    };

    lux.luxApp = function (name, App) {
        lazyApplications[name] = App;
    };

    angular.module('lux.applications', ['lux.services'])

        .directive('luxApp', ['$lux', function ($lux) {
            return {
                restrict: 'AE',
                //
                link: function (scope, element, attrs) {
                    var options = getOptions(attrs),
                        appName = options.luxApp;
                    if (appName) {
                        var App = lazyApplications[appName];
                        if (App) {
                            options.scope = scope;
                            var app = new App(element[0], options);
                        } else {
                            $lux.log.error('Application ' + appName + ' not registered');
                        }
                    } else {
                        $lux.log.error('Application name not available');
                    }
                }
            };
        }]);

    lux.context.ngModules.push('lux.applications');
    var _ = lux._ = {},

    pick = _.pick = function (obj, callback) {
        var picked = {},
            val;
        for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
                val = callback(obj[key], key);
                if (val !== undefined)
                    picked[key] = val;
            }
        }
        return picked;
    };
    var
    //
    ostring = Object.prototype.toString,
    //
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
    },
    //
    // Add a callback for an event to an element
    addEvent = lux.addEvent = function (element, event, callback) {
        var handler = element[event];
        if (!handler)
            element[event] = handler = generateCallbacks();
        if (handler.add)
            handler.add(callback);
    },
    //
    windowResize = lux.windowResize = function (callback) {
        addEvent(window, 'onresize', callback);
    },
    //
    windowHeight = lux.windowHeight = function () {
        return window.innerHeight > 0 ? window.innerHeight : screen.availHeight;
    },
    //
    isAbsolute = new RegExp('^([a-z]+://|//)'),
    //
    // Check if element has tagName tag
    isTag = function (element, tag) {
        element = $(element);
        return element.length === 1 && element[0].tagName === tag.toUpperCase();
    },
    //
    joinUrl = lux.joinUrl = function () {
        var bit, url = '';
        for (var i=0; i<arguments.length; ++i) {
            bit = arguments[i];
            if (bit) {
                var cbit = bit,
                    slash = false;
                // remove fron slashes if url has already some value
                while (url && cbit.substring(0, 1) === '/')
                    cbit = cbit.substring(1);
                // remove end slashes
                while (cbit.substring(cbit.length-1) === '/') {
                    slash = true;
                    cbit = cbit.substring(0, cbit.length-1);
                }
                if (cbit) {
                    if (url && url.substring(url.length-1) !== '/')
                        url += '/';
                    url += cbit;
                    if (slash)
                        url += '/';
                }
            }
        }
        return url;
    },
    //
    isObject = function (o) {
        return ostring.call(o) === '[object Object]';
    },
    //
    getRootAttribute = function (name) {
        var obj = root,
            bits= name.split('.');

        for (var i=0; i<bits.length; ++i) {
            obj = obj[bits[i]];
            if (!obj) break;
        }
        return obj;
    },
    //
    //  getOPtions
    //  ===============
    //
    //  Retrive options for the ``options`` string in ``attrs`` if available.
    //  Used by directive when needing to specify options in javascript rather
    //  than html data attributes.
    getOptions = lux.getOptions = function (attrs) {
        var options;
        if (attrs && typeof attrs.options === 'string') {
            options = getRootAttribute(attrs.options);
            if (typeof options === 'function')
                options = options();
        } else {
            options = {};
        }
        if (isObject(options))
            forEach(attrs, function (value, name) {
                if (name.substring(0, 1) !== '$' && name !== 'options')
                    options[name] = value;
            });
        return options;
    },
    //
    // random generated numbers for a uuid
    s4 = function () {
        return Math.floor((1 + Math.random()) * 0x10000)
                   .toString(16)
                   .substring(1);
    },
    //
    // Extend the initial array with values for other arrays
    extendArray = lux.extendArray = function () {
        if (!arguments.length) return;
        var value = arguments[0],
            push = function (v) {
                value.push(v);
            };
        if (typeof(value.push) === 'function') {
            for (var i=1; i<arguments.length; ++i)
                forEach(arguments[i], push);
        }
        return value;
    },
    //
    //  querySelector
    //  ===================
    //
    //  Simple wrapper for a querySelector
    querySelector = function (elem, query) {
        elem = $(elem);
        if (elem.length)
            return $(elem[0].querySelector(query));
        else
            return elem;
    },
    //
    //    LoadCss
    //  =======================
    //
    //  Load a style sheet link
    loadCss = lux.loadCss = function (filename) {
        var fileref = document.createElement("link");
        fileref.setAttribute("rel", "stylesheet");
        fileref.setAttribute("type", "text/css");
        fileref.setAttribute("href", filename);
        document.getElementsByTagName("head")[0].appendChild(fileref);
    },
    //
    //
    globalEval = lux.globalEval = function(data) {
        if (data) {
            // We use execScript on Internet Explorer
            // We use an anonymous function so that context is window
            // rather than jQuery in Firefox
            (root.execScript || function(data) {
                root["eval"].call(root, data );
            })(data);
        }
    },
    //
    // Simple Slugify function
    slugify = lux.slugify = function (str) {
        str = str.replace(/^\s+|\s+$/g, ''); // trim
        str = str.toLowerCase();

        // remove accents, swap ñ for n, etc
        var from = "àáäâèéëêìíïîòóöôùúüûñç·/_,:;";
        var to   = "aaaaeeeeiiiioooouuuunc------";
        for (var i=0, l=from.length ; i<l ; i++) {
            str = str.replace(new RegExp(from.charAt(i), 'g'), to.charAt(i));
        }

        str = str.replace(/[^a-z0-9 -]/g, '') // remove invalid chars
            .replace(/\s+/g, '-') // collapse whitespace and replace by -
            .replace(/-+/g, '-'); // collapse dashes

        return str;
    },
    //
    now = lux.now = function () {
        return Date.now ? Date.now() : new Date().getTime();
    },
    //
    size = lux.size = function (o) {
        if (!o) return 0;
        if (o.length !== undefined) return o.length;
        var n = 0;
        forEach(o, function () {
            ++n;
        });
        return n;
    };


    var
    //
    // Test for ``_super`` method in a ``Class``.
    //
    // Check http://ejohn.org/blog/simple-javascript-inheritance/
    // for details.
    fnTest = /xyz/.test(function(){var xyz;}) ? /\b_super\b/ : /.*/,
    //
    // Create a method for a derived Class
    create_method = function (type, name, attr, _super) {
        if (typeof attr === "function" && typeof _super[name] === "function" &&
                fnTest.test(attr)) {
            return type.new_attr(name, function() {
                var tmp = this._super;
                // Add a new ._super() method that is the same method
                // but on the super-class
                this._super = _super[name];
                // The method only need to be bound temporarily, so we
                // remove it when we're done executing
                var ret = attr.apply(this, arguments);
                this._super = tmp;
                return ret;
            });
        } else {
            return type.new_attr(name, attr);
        }
    },
    //
    //  Type
    //  -------------

    //  A Type is a factory of Classes. This is the correspondent of
    //  python metaclasses.
    Type = lux.Type = (function (t) {

        t.new_class = function (Caller, attrs) {
            var type = this,
                meta = Caller === type,
                _super = meta ? Caller : Caller.prototype;
            // Instantiate a base class
            Caller.initialising = true;
            var prototype = new Caller();
            delete Caller.initialising;
            //
            // Copy the properties over onto the new prototype
            for (var name in attrs) {
                if (name !== 'Metaclass') {
                    prototype[name] = create_method.call(Caller,
                            type, name, attrs[name], _super);
                }
            }
            if (!meta) {
                //
                // The dummy class constructor
                var constructor = function () {
                    // All construction is actually done in the init method
                    if ( !this.constructor.initialising && this.init ) {
                        this.init.apply(this, arguments);
                    }
                };
                //
                // Populate our constructed prototype object
                constructor.prototype = prototype;
                // Enforce the constructor to be what we expect
                constructor.prototype.constructor = constructor;
                // And make this class extendable
                constructor.extend = Caller.extend;
                //
                return constructor;
            } else {
                for (name in _super) {
                    if (prototype[name] === undefined) {
                        prototype[name] = _super[name];
                    }
                }
                return prototype;
            }
        };
        //
        t.new_attr = function (name, attr) {
            return attr;
        };
        // Create a new Class that inherits from this class
        t.extend = function (attrs) {
            return t.new_class(this, attrs);
        };
        //
        return t;
    }(function(){})),
    //
    //  ## Class

    //  Lux base class.
    //  The `extend` method is the most important function of this object.
    Class = lux.Class = (function (c) {
        c.__class__ = Type;
        //
        c.extend = function (attrs) {
            var type = attrs.Metaclass || this.__class__;
            var cls = type.new_class(this, attrs);
            cls.__class__ = type;
            return cls;
        };
        //
        return c;
    }(function() {}));
    //  Lux Api service factory for angular
    //  ---------------------------------------
    angular.module('lux.api', [])
        //
        .value('ApiTypes', {})
        //
        .service('$lux', ['$location', '$q', '$http', '$log', '$timeout', 'ApiTypes',
                function ($location, $q, $http, $log, $timeout, ApiTypes) {
            var $lux = this;

            this.location = $location;
            this.log = $log;
            this.http = $http;
            this.q = $q;
            this.timeout = $timeout;
            //  Create a client api
            //  -------------------------
            //
            //  context: an api name or an object containing, name, url and type.
            //
            //  name: the api name
            //  url: the api base url
            //  type: optional api type (default is ``lux``)
            this.api = function (context) {
                if (Object(context) !== context) {
                    context = {name: context};
                }
                var Api = ApiTypes[context.type || 'lux'];
                if (!Api)
                    $lux.log.error('Api provider "' + context.name + '" is not available');
                else {
                    return new Api(context.name, context.url, context.options, $lux);
                }
            };
            //
            this.registerApi = function (name, object, inheritFrom) {
                var Base = inheritFrom ? ApiTypes[inheritFrom] : ApiClient;
                ApiTypes[name] = Base.extend(object);
                return ApiTypes[name];
            };
        }]);
    //
    function wrapPromise (promise) {
        promise.success = function(fn) {
            return wrapPromise(this.then(function(response) {
                return fn(response.data, response.status, response.headers);
            }));
        };

        promise.error = function(fn) {
            return wrapPromise(this.then(null, function(response) {
                return fn(response.data, response.status, response.headers);
            }));
        };

        return promise;
    }
    //
    //  Lux API Interface for REST
    //
    var ApiClient = lux.ApiClient = Class.extend({
        //
        //  Object containing the urls for the api.
        //  If not given, the object will be loaded via the ``context.apiUrl``
        //  variable.
        apiUrls: lux.context.apiUrls,
        //
        init: function (name, url, options, $lux) {
            this.name = name;
            this.options = options || {};
            this.$lux = $lux;
            this.auth = null;
            this._url = url;
        },
        //
        // Can be used to manipulate the url
        url: function (urlparams) {
            if (urlparams && urlparams.id)
                return this._url + '/' + urlparams.id;
            else
                return this._url;
        },
        //
        //  Handle authentication
        //
        //  By default does nothing
        authentication: function (request) {
            this.auth = {};
            this.call(request);
        },
        //
        // Add Authentication to call options
        addAuth: function (request) {

        },
        //
        // Build the object used by $http when executing the api call
        httpOptions: function (request) {
            var options = request.options;
            if (!options.url)
                options.url = this.url(request.urlparams);
            return options;
        },
        //
        //
        // Perform the actual request and return a promise
        //  method: HTTP method
        //  urlparams:
        //  opts: object passed to
        request: function (method, urlparams, opts, data) {
            // handle urlparams when not an object
            if (urlparams && urlparams!==Object(urlparams))
                urlparams = {id: urlparams};

            var d = this.$lux.q.defer(),
                //
                promise = d.promise,
                //
                request = {
                    deferred: d,
                    //
                    options: extend({'method': method, 'data': data}, opts),
                    //
                    'urlparams': urlparams,
                    //
                    api: this,
                    //
                    error: function (data, status, headers) {
                        if (isString(data)) {
                            data = {error: true, message: data};
                        }
                        d.reject({
                            'data': data,
                            'status': status,
                            'headers': headers
                        });
                    },
                    //
                    success: function (data, status, headers) {
                        d.resolve({
                            'data': data,
                            'status': status,
                            'headers': headers
                        });
                    }
                };
            //
            this.call(request);
            //
            return wrapPromise(promise);
        },
        //
        //  Get a single element
        //  ---------------------------
        get: function (urlparams, options) {
            return this.request('GET', urlparams, options);
        },
        //  Create or update a model
        //  ---------------------------
        put: function (model, options) {
            if (model.id) {
                return this.request('POST', {id: model.id}, options, model);
            } else {
                return this.request('POST', null, options, model);
            }
        },
        //  Get a list of models
        //  -------------------------
        getList: function (options) {
            return this.request('GET', null, options);
        },
        //
        getPage: function (page, state, stateParams) {
            return page;
        },
        //
        getItems: function (page, state, stateParams) {
            if (!lux.size(stateParams))
                return this.getList();
        },
        //
        //  Execute an API call for a given request
        //  This method is hardly used directly, the ``request`` method is normally used.
        //
        //      request: a request object obtained from the ``request`` method
        call: function (request) {
            var $lux = this.$lux,
                url = request.options.url || this._url;
            //
            if (!url && ! this.name) {
                return request.error('api should have url or name');
            }

            if (!url) {
                if (this.apiUrls) {
                    this._url = url = this.apiUrls[this.name] || this.apiUrls[this.name + '_url'];
                    //
                    // No api url!
                    if (url)
                        return request.error('Could not find a valid url for ' + this.name);
                    //
                } else if (lux.context.apiUrl) {
                    // Fetch the api urls
                    var self = this;
                    $lux.log.info('Fetching api info');
                    return $lux.http.get(lux.context.apiUrl).success(function (resp) {
                        self.apiUrls = resp;
                        self.call(request);
                    }).error(request.error);
                    //
                } else
                    return request.error('Api url not available');
            }
            //
            // Fetch authentication token?
            if (!this.auth)
                return this.authentication(request);
            //
            // Add authentication
            this.addAuth(request);
            //
            var options = this.httpOptions(request);
            //
            if (options.url) {
                $lux.log.info('Executing HTTP ' + options.method + ' request @ ' + options.url);
                $lux.http(options).success(request.success).error(request.error);
            }
            else
                request.error('Api url not available');
        }
    });

    //
    //  Lux web and api handler
    //  ----------------------
    angular.module('lux.web.api', ['lux.api'])

        .run(['$lux', function ($lux) {
            //
            var csrf = {},
                name = $(document.querySelector("meta[name=csrf-param]")).attr('content'),
                csrf_token = $(document.querySelector("meta[name=csrf-token]")).attr('content');

            if (name && csrf_token)
                csrf[name] = csrf_token;

            // A post method with CSRF parameter
            $lux.post = function (url, data, cfg) {
                var ct = cfg ? cfg.contentType : null,
                    fd = this.formData(ct);
                return this.http.post(url, fd(data), cfg);
            };

            //
            // Change the form data depending on content type
            $lux.formData = function (contentType) {

                return function (data) {
                    data = extend(data || {}, csrf);
                    if (contentType === 'application/x-www-form-urlencoded')
                        return $.param(data);
                    else if (contentType === 'multipart/form-data') {
                        var fd = new FormData();
                        forEach(data, function (value, key) {
                            fd.append(key, value);
                        });
                        return fd;
                    } else {
                        return data;
                    }
                };
            };
            //
            $lux.registerApi('lux', {
                //
                authentication: function (request) {
                    var self = this;
                    //
                    if (lux.context.user_token) {
                        self.auth = {user_token: lux.context.user_token};
                    } else if (lux.context.user) {
                        $lux.log.info('Fetching authentication token');
                        //
                        $lux.post('/_token').success(function (data) {
                            lux.context.user_token = data.token;
                            self.auth = {user_token: lux.context.user_token};
                            self.call(request);
                        }).error(request.error);
                        //
                        return request.deferred.promise;
                    } else {
                        self.auth = {};
                    }
                    self.call(request);
                },
                //
                addAuth: function (request) {
                    //
                    // Add authentication token
                    if (lux.context.user_token) {
                        var headers = request.options.headers;
                        if (!headers)
                            request.options.headers = headers = {};

                        headers.Authorization = 'Bearer ' + lux.context.user_token;
                    }
                },
            });
        }]);

    //
    //  Hash scrolling service
    angular.module('lux.scroll', [])
        //
        // Switch off scrolling managed by angular
        //.value('$anchorScroll', angular.noop)
        //
        .value('scrollDefaults', {
            // Time to complete the scrolling (seconds)
            time: 1,
            // Offset relative to hash links
            offset: 0,
            // Number of frames to use in the scroll transition
            frames: 25,
            // If true, scroll to top of the page when hash is empty
            topPage: true,
            //
            scrollTargetClass: 'scroll-target',
            //
            scrollTargetClassFinish: 'finished'
        })
        //
        // Switch off scrolling managed by angular
        .config(['$anchorScrollProvider', function ($anchorScrollProvider) {
            $anchorScrollProvider.disableAutoScrolling();
        }])
        //
        .run(['$rootScope', '$location', '$log', '$timeout', 'scrollDefaults',
                function(scope, location, log, timer, scrollDefaults) {
            //
            var target = null,
                scroll = scope.scroll = extend({}, scrollDefaults, scope.scroll);
            //
            scroll.browser = true;
            scroll.path = false;
            //
            scope.$location = location;
            //
            // This is the first event triggered when the path location changes
            scope.$on('$locationChangeSuccess', function() {
                if (!scroll.path) {
                    scroll.browser = true;
                    _clear();
                }
            });

            // Watch for path changes and check if back browser button was used
            scope.$watch(function () {
                return location.path();
            }, function (newLocation, oldLocation) {
                if (!scroll.browser) {
                    scroll.path = newLocation !== oldLocation;
                    if (!scroll.path)
                        scroll.browser = true;
                } else
                    scroll.path = false;
            });

            // Watch for hash changes
            scope.$watch(function () {
                return location.hash();
            }, function (hash) {
                if (!(scroll.path || scroll.browser))
                    toHash(hash);
            });

            scope.$on('$viewContentLoaded', function () {
                var hash = location.hash();
                if (!scroll.browser)
                    toHash(hash, 0);
            });
            //
            function toHash (hash, delay) {
                timer(function () {
                    _toHash(hash, delay);
                });
            }
            //
            function _toHash (hash, delay) {
                if (target)
                    return;
                if (!hash && !scroll.topPage)
                    return;
                // set the location.hash to the id of
                // the element you wish to scroll to.
                if (typeof(hash) === 'string') {
                    var highlight = true;
                    if (hash.substring(0, 1) === '#')
                        hash = hash.substring(1);
                    if (hash)
                        target = document.getElementById(hash);
                    else {
                        highlight = false;
                        target = document.getElementsByTagName('body');
                        target = target.length ? target[0] : null;
                    }
                    if (target) {
                        _clearTargets();
                        target = $(target);
                        if (highlight)
                            target.addClass(scroll.scrollTargetClass)
                                  .removeClass(scroll.scrollTargetClassFinish);
                        log.info('Scrolling to target #' + hash);
                        _scrollTo(delay);
                    }
                }
            }

            function _clearTargets () {
                forEach(document.querySelectorAll('.' + scroll.scrollTargetClass), function (el) {
                    $(el).removeClass(scroll.scrollTargetClass);
                });
            }

            function _scrollTo (delay) {
                var stopY = elmYPosition(target[0]) - scroll.offset;

                if (delay === 0) {
                    window.scrollTo(0, stopY);
                    _finished();
                } else {
                    var startY = currentYPosition(),
                        distance = stopY > startY ? stopY - startY : startY - stopY,
                        step = Math.round(distance / scroll.frames);

                    if (delay === null || delay === undefined) {
                        delay = 1000*scroll.time/scroll.frames;
                        if (distance < 200)
                            delay = 0;
                    }
                    _nextScroll(startY, delay, step, stopY);
                }
            }

            function _nextScroll (y, delay, stepY, stopY) {
                var more = true,
                    y2, d;
                if (y < stopY) {
                    y2 = y + stepY;
                    if (y2 >= stopY) {
                        more = false;
                        y2 = stopY;
                    }
                    d = y2 - y;
                } else {
                    y2 = y - stepY;
                    if (y2 <= stopY) {
                        more = false;
                        y2 = stopY;
                    }
                    d = y - y2;
                }
                timer(function () {
                    window.scrollTo(0, y2);
                    if (more)
                        _nextScroll(y2, delay, stepY, stopY);
                    else {
                        _finished();
                    }
                }, delay);
            }

            function _finished () {
                // Done with it - set the hash in the location
                // location.hash(target.attr('id'));
                if (target.hasClass(scroll.scrollTargetClass))
                    target.addClass(scroll.scrollTargetClassFinish);
                target = null;
                _clear();
            }

            function _clear (delay) {
                if (delay === undefined) delay = 0;
                timer(function () {
                    log.info('Reset scrolling');
                    scroll.browser = false;
                    scroll.path = false;
                }, delay);
            }

            function currentYPosition() {
                // Firefox, Chrome, Opera, Safari
                if (window.pageYOffset) {
                    return window.pageYOffset;
                }
                // Internet Explorer 6 - standards mode
                if (document.documentElement && document.documentElement.scrollTop) {
                    return document.documentElement.scrollTop;
                }
                // Internet Explorer 6, 7 and 8
                if (document.body.scrollTop) {
                    return document.body.scrollTop;
                }
                return 0;
            }

            /* scrollTo -
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
            function elmYPosition(node) {
                var y = node.offsetTop;
                while (node.offsetParent && node.offsetParent != document.body) {
                    node = node.offsetParent;
                    y += node.offsetTop;
                }
                return y;
            }

        }]);
    //
    //  Lux Static site JSON API
    //  ------------------------
    //
    //  Api used by static sites
    angular.module('lux.static.api', ['lux.api'])

        .run(['$lux', function ($lux) {
            var pageCache = {};

            $lux.registerApi('static', {
                //
                url: function (urlparams) {
                    var url = this._url,
                        name = urlparams ? urlparams.slug : null;
                    if (url.substring(url.length-5) === '.json')
                        return url;
                    if (url.substring(url.length-1) !== '/')
                        url += '/';
                    url += name || 'index';
                    if (url.substring(url.length-5) === '.html')
                        url = url.substring(0, url.length-5);
                    else if (url.substring(url.length-1) === '/')
                        url += 'index';
                    if (url.substring(url.length-5) !== '.json')
                        url += '.json';
                    return url;
                },
                //
                getPage: function (page, state, stateParams) {
                    var href = lux.stateHref(state, page.name, stateParams),
                        data = pageCache[href];
                    if (data)
                        return data;
                    //
                    return this.get(stateParams).success(function (data) {
                        pageCache[href] = data;
                        forEach(data.require_css, function (css) {
                            loadCss(css);
                        });
                        if (data.require_js) {
                            var defer = $lux.q.defer();
                            require(rcfg.min(data.require_js), function () {
                                // let angular resolve its queue if it needs to
                                defer.resolve(data);
                            });
                            return defer.promise;
                        } else
                            return data;
                    });
                },
                //
                getItems: function (page, state, stateParams) {
                    if (page.apiItems)
                        return this.getList({url: this._url + '.json'});
                }
            });
        }]);

angular.module('templates-page', ['page/breadcrumbs.tpl.html']);

angular.module("page/breadcrumbs.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("page/breadcrumbs.tpl.html",
    "<ol class=\"breadcrumb\">\n" +
    "    <li ng-repeat=\"step in steps\" ng-class=\"{active: step.last}\">\n" +
    "        <a ng-if=\"!step.last\" href=\"{{step.href}}\">{{step.label}}</a>\n" +
    "        <span ng-if=\"step.last\">{{step.label}}</span>\n" +
    "    </li>\n" +
    "</ol>");
}]);

    //  Lux Page
    //  ==============
    //
    //  Design to work with the ``lux.extension.angular``
    angular.module('lux.page', ['lux.services', 'lux.form', 'lux.scroll', 'templates-page'])
        //
        .service('pageService', ['$lux', 'dateFilter', function ($lux, dateFilter) {

            this.addInfo = function (page, $scope) {
                if (!page)
                    return $lux.log.error('No page, cannot add page information');
                if (page.head && page.head.title) {
                    document.title = page.head.title;
                }
                if (page.author) {
                    if (page.author instanceof Array)
                        page.authors = page.author.join(', ');
                    else
                        page.authors = page.author;
                }
                var date;
                if (page.date) {
                    try {
                        date = new Date(page.date);
                    } catch (e) {
                        $lux.log.error('Could not parse date');
                    }
                    page.date = date;
                    page.dateText = dateFilter(date, $scope.dateFormat);
                }
                page.toString = function () {
                    return this.name || this.url || '<noname>';
                };

                return page;
            };

            this.formatDate = function (dt, format) {
                if (!dt)
                    dt = new Date();
                return dateFilter(dt, format || 'yyyy-MM-ddTHH:mm:ss');
            };
        }])
        //
        .controller('Page', ['$scope', '$log', '$lux', 'pageService', function ($scope, log, $lux, pageService) {
            //
            $lux.log.info('Setting up angular page');
            //
            var page = $scope.page;
            // If the page is a string, retrieve it from the pages object
            if (typeof page === 'string')
                page = $scope.pages ? $scope.pages[page] : null;
            $scope.page = pageService.addInfo(page, $scope);
            //
            $scope.togglePage = function ($event) {
                $event.preventDefault();
                $event.stopPropagation();
                this.link.active = !this.link.active;
            };

            $scope.loadPage = function ($event) {
                $scope.page = this.link;
            };

            $scope.activeLink = function (url) {
                var loc;
                if (isAbsolute.test(url))
                    loc = $lux.location.absUrl();
                else
                    loc = window.location.pathname;
                var rest = loc.substring(url.length),
                    base = loc.substring(0, url.length),
                    folder = url.substring(url.length-1) === '/';
                return base === url && (folder || (rest === '' || rest.substring(0, 1) === '/'));
            };

            //
            $scope.$on('animIn', function() {
                log.info('Page ' + page.toString() + ' animation in');
            });
            $scope.$on('animOut', function() {
                log.info('Page ' + page.toString() + ' animation out');
            });
        }])

        .service('$breadcrumbs', [function () {

            this.crumbs = function () {
                var loc = window.location,
                    path = loc.pathname,
                    steps = [],
                    last = {
                        href: loc.origin
                    };
                if (last.href.length >= lux.context.url.length)
                    steps.push(last);

                path.split('/').forEach(function (name) {
                    if (name) {
                        last = {
                            label: name,
                            href: joinUrl(last.href, name+'/')
                        };
                        if (last.href.length >= lux.context.url.length)
                            steps.push(last);
                    }
                });
                if (steps.length) {
                    last = steps[steps.length-1];
                    if (path.substring(path.length-1) !== '/' && last.href.substring(last.href.length-1) === '/')
                        last.href = last.href.substring(0, last.href.length-1);
                    last.last = true;
                    steps[0].label = 'Home';
                }
                return steps;
            };
        }])
        //
        //  Directive for displaying breadcrumbs navigation
        .directive('breadcrumbs', ['$breadcrumbs', '$rootScope', function ($breadcrumbs, $rootScope) {
            return {
                restrict: 'AE',
                replace: true,
                templateUrl: "page/breadcrumbs.tpl.html",
                link: {
                    post: function (scope) {
                        var renderBreadcrumb = function() {
                            scope.steps = $breadcrumbs.crumbs();
                        };

                        $rootScope.$on('$viewContentLoaded', function () {
                            renderBreadcrumb();
                        });

                        renderBreadcrumb();
                    }
                }
            };
        }]);


    angular.module('lux.router', ['lux.page'])
        .config(['$provide', '$locationProvider', function ($provide, $locationProvider) {
            if (lux.context.html5mode) {
                $locationProvider.html5Mode(true);
                lux.context.targetLinks = true;
            }
            $locationProvider.hashPrefix(lux.context.hashPrefix);
        }])
        //
        //  Convert all internal links to have a target so that the page reload
        .directive('page', ['$log', '$timeout', function (log, timer) {
            return {
                link: function (scope, element) {
                    var toTarget = function () {
                            log.info('Transforming links into targets');
                            forEach($(element)[0].querySelectorAll('a'), function(link) {
                                link = $(link);
                                if (!link.attr('target'))
                                    link.attr('target', '_self');
                            });
                        };
                    // Put the toTarget function into the queue so that it is
                    // processed after all
                    timer(toTarget, 0);
                }
            };
        }]);
    //
    //  UI-Routing
    //
    //  Configure ui-Router using lux routing objects
    //  Only when context.html5mode is true
    //  Python implementation in the lux.extensions.angular Extension
    //

    // Hack for delaing with ui-router state.href
    // TODO: fix this!
    var stateHref = lux.stateHref = function (state, State, Params) {
        if (Params) {
            var url = state.href(State, Params);
            return url.replace(/%2F/g, '/');
        } else {
            return state.href(State);
        }
    };

    angular.module('lux.ui.router', ['lux.page', 'ui.router'])
        //
        .run(['$rootScope', '$state', '$stateParams', function (scope, $state, $stateParams) {
            //
            // It's very handy to add references to $state and $stateParams to the $rootScope
            scope.$state = $state;
            scope.$stateParams = $stateParams;
        }])
        //
        .config(['$locationProvider', '$stateProvider', '$urlRouterProvider', '$anchorScrollProvider',
            function ($locationProvider, $stateProvider, $urlRouterProvider, $anchorScrollProvider) {

            var
            hrefs = lux.context.hrefs,
            pages = lux.context.pages,
            pageCache = lux.context.cachePages ? {} : null,
            //
            state_config = function (page) {
                var main = {
                    //
                    resolve: {
                        // Fetch page information
                        page: ['$lux', '$state', '$stateParams', function ($lux, state, stateParams) {
                            if (page.api) {
                                var api = $lux.api(page.api);
                                if (api)
                                    return api.getPage(page, state, stateParams);
                            }
                            return page;
                        }],
                        // Fetch items if needed
                        items: ['$lux', '$state', '$stateParams', function ($lux, state, stateParams) {
                            if (page.api) {
                                var api = $lux.api(page.api);
                                if (api)
                                    return api.getItems(page, state, stateParams);
                            }
                        }],
                    },
                    //
                    controller: page.controller
                };

                if (page.template)
                    main.template = page.template;
                else if (page.templateUrl)
                    main.templateUrl = page.templateUrl;

                return {
                    url: page.url,
                    //
                    views: {
                        main: main
                    }
                };
            };

            $locationProvider.html5Mode(lux.context.html5mode).hashPrefix(lux.context.hashPrefix);
            //
            forEach(hrefs, function (href) {
                var page = pages[href];
                // Redirection
                if (page.redirectTo)
                    $urlRouterProvider.when(page.url, page.redirectTo);
                else {
                    var name = page.name;
                    if (!name) {
                        name = 'home';
                    }
                    $stateProvider.state(name, state_config(page));
                }
            });
        }])
        //
        .controller('Html5', ['$scope', '$state', 'pageService', 'page', 'items',
            function ($scope, $state, pageService, page, items) {
                $scope.items = items ? items.data : null;
                $scope.page = pageService.addInfo(page, $scope);
            }])
        //
        .directive('dynamicPage', ['$compile', '$log', function ($compile, log) {
            return {
                link: function (scope, element, attrs) {
                    scope.$on('$stateChangeSuccess', function () {
                        var page = scope.page;
                        if (page.html && page.html.main) {
                            element[0].innerHTML = page.html.main;
                            var scripts= element[0].getElementsByTagName('script');
                            // Execute scripts in the loaded html
                            forEach(scripts, function (js) {
                                globalEval(js.innerHTML);
                            });
                            log.info('Compiling new html content');
                            $compile(element.contents())(scope);
                            // load required scripts if necessary
                            lux.loadRequire();
                        }
                    });
                }
            };
        }]);

    // Default Form processing function
    // If a submit element (input.submit or button) does not specify
    // a ``click`` entry, this function is used
    lux.processForm = function (e) {
        e.preventDefault();
        e.stopPropagation();
        var form = this[this.formName],
            model = this[this.formModelName],
            attrs = this.formAttrs,
            target = attrs.action,
            apiname = attrs.apiname,
            scope = this,
            FORMKEY = scope.formAttrs.FORMKEY,
            $lux = this.$lux,
            promise,
            api;
        //
        // Flag the form as submitted
        form.submitted = true;
        if (form.$invalid) {
            return;
        }

        // Get the api information
        if (!target && apiname) {
            api = $lux.api(apiname);
            if (!api)
                $lux.log.error('Could not find api url for ' + apiname);
        }

        this.formMessages = {};
        //
        if (target) {
            var enctype = attrs.enctype || '',
                ct = enctype.split(';')[0],
                options = {
                    url: target,
                    method: attrs.method || 'POST',
                    data: model,
                    transformRequest: $lux.formData(ct),
                };
            // Let the browser choose the content type
            if (ct === 'application/x-www-form-urlencoded' || ct === 'multipart/form-data') {
                options.headers = {
                    'content-type': undefined
                };
            }
            promise = $lux.http(options);
        } else if (api) {
            promise = api.put($scope.formModel);
        } else {
            $lux.log.error('Could not process form. No target or api');
            return;
        }
        //
        promise.success(function(data, status) {
            if (data.messages) {
                scope.addMessages(data.messages);
            } else if (api) {
                // Created
                if (status === 201) {
                    scope.formMessages[FORMKEY] = [{message: 'Succesfully created'}];
                } else {
                    scope.formMessages[FORMKEY] = [{message: 'Succesfully updated'}];
                }
            } else {
                window.location.href = data.redirect || '/';
            }
        }).error(function(data, status, headers) {
            var messages, msg;
            if (data) {
                messages = data.messages;
                if (!messages) {
                    msg = data.message;
                    if (!msg) {
                        status = status || data.status || 501;
                        msg = 'Server error (' + data.status + ')';
                    }
                    messages = {};
                    scope.formMessages[FORMKEY] = [{message: msg, error: true}];
                }
            } else {
                status = status || 501;
                msg = 'Server error (' + data.status + ')';
                messages = {};
                scope.formMessages[FORMKEY] = [{message: msg, error: true}];
            }
        });
    };


    // Default form module for lux
    angular.module('lux.form', ['lux.services'])
        //
        .constant('formDefaults', {
            // Default form processing function
            processForm: lux.processForm,
            // Default layout
            layout: 'default',
            // for horizontal layout
            labelSpan: 2,
            showLabels: true,
            novalidate: true,
            //
            formErrorClass: 'form-error',
            FORMKEY: 'm__form'
        })
        //
        // The formService is a reusable component for redering form fields
        .service('standardForm', ['$log', '$http', '$document', '$templateCache', 'formDefaults',
                function (log, $http, $document, $templateCache, formDefaults) {

            var supported = {
                    //  Text-based elements
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
                    'form': {element: 'form', editable: false, textBased: false},
                    'radio': {element: 'div', editable: false, textBased: false},
                    //  Non-editables (mostly buttons)
                    'button': {element: 'button', type: 'button', editable: false, textBased: false},
                    'hidden': {element: 'input', type: 'hidden', editable: false, textBased: false},
                    'image': {element: 'input', type: 'image', editable: false, textBased: false},
                    'legend': {element: 'legend', editable: false, textBased: false},
                    'reset': {element: 'button', type: 'reset', editable: false, textBased: false},
                    'submit': {element: 'button', type: 'submit', editable: false, textBased: false}
                },
                //
                baseAttributes = ['id', 'name', 'title', 'style'],
                inputAttributes = extendArray([], baseAttributes, ['disabled', 'type', 'value', 'placeholder']),
                textareaAttributes = extendArray([], baseAttributes, ['disabled', 'placeholder', 'rows', 'cols']),
                buttonAttributes = extendArray([], baseAttributes, ['disabled']),
                formAttributes = extendArray([], baseAttributes, ['accept-charset', 'action', 'autocomplete',
                                                                  'enctype', 'method', 'novalidate', 'target']),
                validationAttributes = ['minlength', 'maxlength', 'min', 'max', 'required'],
                ngAttributes = ['disabled', 'minlength', 'maxlength', 'required'];

            extend(this, {
                name: 'default',
                //
                className: '',
                //
                inputGroupClass: 'form-group',
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
                    var self = this,
                        thisField = scope.field,
                        info = supported[thisField.type],

                        renderer;

                    scope.info = info;

                    if (info)
                        renderer = this[info.element];

                    if (!renderer)
                        renderer = this.renderNotSupported;

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
                            else {
                                if (value === true) value = '';
                                element.attr(name, value);
                            }
                        } else if (name.substring(0, 5) === 'data-') {
                            element.attr(name, value);
                        }
                    });
                    return element;
                },
                //
                renderNotSupported: function (scope) {
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
                radio: function (scope) {
                    this.fillDefaults(scope);

                    var field = scope.field,
                        info = scope.info,
                        input = angular.element($document[0].createElement(info.element)).addClass(this.inputClass),
                        label = angular.element($document[0].createElement('label')),
                        element = angular.element($document[0].createElement('div')).addClass(this.element);

                    input.attr('ng-model', scope.formModelName + '.' + field.name);

                    forEach(InputAttributes, function (name) {
                        if (field[name]) input.attr(name, field[name]);
                    });

                    return this.onChange(scope, element.append(label.append(input)));
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
                    input.attr('ng-model', scope.formModelName + '.' + field.name);

                    if (!field.showLabels) {
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

                    if (this.inputGroupClass) {
                        element = angular.element($document[0].createElement('div')).addClass(this.inputGroupClass);
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
                        info = scope.info,
                        element = this.input(scope),
                        select = this._select(info.element, element);
                    forEach(field.options, function (opt) {
                        if (typeof(opt) === 'string') {
                            opt = {'value': opt};
                        } else if (isArray(opt)) {
                            opt = {'value': opt[0], 'repr': opt[1] || opt[0]};
                        }
                        opt = $($document[0].createElement('option'))
                                .attr('value', opt.value).html(opt.repr || opt.value);
                        select.append(opt);
                    });
                    return this.onChange(scope, element);
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
                        clickname = name + 'Click';
                    //
                    // scope function
                    scope[clickname] = function (e) {
                        var callback = formDefaults.processForm;
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
                        dirty = [scope.formName, field.name, '$dirty'].join('.'),
                        invalid = [scope.formName, field.name, '$invalid'].join('.'),
                        error = [scope.formName, field.name, '$error'].join('.') + '.',
                        input = $(element[0].querySelector(scope.info.element)),
                        p = $($document[0].createElement('p'))
                                .attr('ng-show', '(' + submitted + ' || ' + dirty + ') && ' + invalid)
                                .addClass('text-danger')
                                .addClass(scope.formErrorClass)
                                .html('{{formErrors.' + field.name + '}}'),
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
                    var errors = p.children().length;
                    if (errors === (field.required ? 1 : 0)) {
                        var name = '$invalid';
                        if (errors)
                            name += ' && !' + [scope.formName, field.name, '$error.required'].join('.');
                        p.append(this.fieldErrorElement(scope, name, self.errorMessage(scope, 'invalid')));
                    }
                    return element.append(p);
                },
                //
                fieldErrorElement: function (scope, name, msg) {
                    var field = scope.field,
                        value = [scope.formName, field.name, name].join('.');

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
                    return scope.field.label + " is required";
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
        .service('horizontalForm', ['$document', 'standardForm', function ($document, standardForm) {
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
                inputTemplateUrl: "forms/inlineInput.tpl.html",
                checkTemplateUrl: "forms/inlineCheck.tpl.html"
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

                    scope.addMessages = function (messages) {
                        forEach(messages, function (messages, field) {
                            scope.formMessages[field] = messages;
                        });
                    };

                    scope.fireFieldChange = function (name) {
                        var obj = {
                            form: formmodel,
                            field: name
                        };
                        // Triggered wvery time a form field changes
                        scope.$broadcast('fieldChange', obj);
                        scope.$emit('formFieldChange', obj);
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
                //
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
        });

angular.module('templates-users', ['users/messages.tpl.html']);

angular.module("users/messages.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("users/messages.tpl.html",
    "<div ng-repeat=\"message in messages\" class=\"alert alert-dismissible\"\n" +
    "ng-class=\"messageClass[message.level]\">\n" +
    "<button type=\"button\" class=\"close\" data-dismiss=\"alert\" ng-click=\"dismiss($event, message)\">\n" +
    "    <span aria-hidden=\"true\">&times;</span>\n" +
    "    <span class=\"sr-only\">Close</span>\n" +
    "</button>\n" +
    "<span ng-bind-html=\"message.html\"></span>\n" +
    "</div>");
}]);


    // Controller for User.
    // This controller can be used by eny element, including forms
    angular.module('lux.users', ['lux.form', 'templates-users'])

        .run(['$rootScope', '$lux', function (scope, $lux) {

            // logout via post method
            scope.logout = function(e, url) {
                e.preventDefault();
                e.stopPropagation();
                $lux.post(url).success(function (data) {
                    if (data.redirect)
                        window.location.replace(data.redirect);
                });
            };

        }])
        //
        // Directive for displaying page messages
        //
        //  <div data-options='sitemessages' data-page-messages></div>
        //  <script>
        //      sitemessages = {
        //          messages: [...],
        //          dismissUrl: (Optional url to use when dismissing a message)
        //      };
        //  </script>
        .directive('pageMessages', ['$lux', '$sce', function ($lux, $sce) {

            return {
                restrict: 'AE',
                templateUrl: "users/messages.tpl.html",
                scope: {},
                link: function (scope, element, attrs) {
                    scope.messageClass = {
                        info: 'alert-info',
                        success: 'alert-success',
                        warning: 'alert-warning',
                        danger: 'alert-danger',
                        error: 'alert-danger'
                    };
                    //
                    // Dismiss a message
                    scope.dismiss = function (e, m) {
                        var target = e.target;
                        while (target && target.tagName !== 'DIV')
                            target = target.parentNode;
                        $(target).remove();
                        $lux.post('/_dismiss_message', {message: m});
                    };
                    var messages = getOptions(attrs);
                    scope.messages = [];
                    forEach(messages, function (message) {
                        if (message) {
                            if (typeof(message) === 'string')
                                message = {body: message};
                            message.html = $sce.trustAsHtml(message.body);
                        }
                        scope.messages.push(message);
                    });
                }
            };
        }])

        .directive('userForm', ['formRenderer', function (renderer) {
            //
            renderer._createElement = renderer.createElement;

            // Override createElement to add passwordVerify directive in the password_repead input
            renderer.createElement = function (scope) {

                var element = this._createElement(scope),
                    field = scope.field,
                    other = field['data-check-repeat'] || field['check-repeat'];

                if (other) {
                    var msg = field.errorMessage || (other + " doesn't match"),
                        errors = $(element[0].querySelector('.' + scope.formErrorClass));
                    if (errors.length)
                        errors.html('').append(renderer[field.layout].fieldErrorElement(
                            scope, '$error.repeat', msg));
                }
                return element;
            };

            return renderer.directive();
        }])

        .controller('UserController', ['$scope', '$lux', function (scope, lux) {
            // Model for a user when updating

            // Unlink account for a OAuth provider
            scope.unlink = function(e, name) {
                e.preventDefault();
                e.stopPropagation();
                var url = '/oauth/' + name + '/remove';
                $.post(url).success(function (data) {
                    if (data.success)
                        $route.reload();
                });
            };
        }]);
    lux.loader = angular.module('lux.loader', []);

    lux.loader
        .value('context', lux.context)
        //
        .config(['$controllerProvider', function ($controllerProvider) {
            lux.loader.cp = $controllerProvider;
        }])
        //
        .run(['$rootScope', '$log', '$timeout', 'context', function (scope, $log, $timeout, context) {
            $log.info('Extend root scope with context');
            extend(scope, context);
            scope.$timeout = $timeout;
            scope.$log = $log;
        }]);
    //
    // Bootstrap the document
    lux.bootstrap = function (name, modules) {
        //
        // actual bootstrapping function
        function _bootstrap() {
            //
            // Resolve modules to load
            if (!isArray(modules))
                modules = [];
            if (lux.context.uiRouter) {
                modules.push(lux.context.uiRouter);
                // Remove seo view, we don't want to bootstrap it
                $(document.querySelector('#seo-view')).remove();
            }
            else {
                modules.push('lux.router');
            }
            // Add all modules from context
            forEach(lux.context.ngModules, function (mod) {
                modules.push(mod);
            });
            modules.splice(0, 0, 'lux.loader');
            angular.module(name, modules);
            angular.bootstrap(document, [name]);
            //
            if (!lux.context.uiRouter)
                lux.loadRequire();
        }

        if (!angular_bootstrapped) {
            angular_bootstrapped = true;
            //
            $(document).ready(function() {
                _bootstrap();
            });
        }
    };

angular.module('templates-blog', ['blog/header.tpl.html', 'blog/pagination.tpl.html']);

angular.module("blog/header.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("blog/header.tpl.html",
    "<h2 data-ng-bind=\"page.title\"></h2>\n" +
    "<p class=\"small\">by {{page.authors}} on {{page.dateText}}</p>\n" +
    "<p class=\"lead storyline\">{{page.description}}</p>");
}]);

angular.module("blog/pagination.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("blog/pagination.tpl.html",
    "<ul class=\"media-list\">\n" +
    "    <li ng-repeat=\"post in items\" class=\"media\" data-ng-controller='BlogEntry'>\n" +
    "        <a href=\"{{post.html_url}}\" ng-attr-target=\"{{postTarget}}\">\n" +
    "            <div class=\"clearfix\">\n" +
    "                <img ng-src=\"{{post.image}}\" class=\"hidden-xs post-image\" alt=\"{{post.title}}\">\n" +
    "                <img ng-src=\"{{post.image}}\" alt=\"{{post.title}}\" class=\"visible-xs post-image-xs center-block\">\n" +
    "                <div class=\"post-body hidden-xs\">\n" +
    "                    <h3 class=\"media-heading\">{{post.title || \"Untitled\"}}</h3>\n" +
    "                    <p data-ng-if=\"post.description\">{{post.description}}</p>\n" +
    "                    <p class=\"text-info small\">by {{post.authors}} on {{post.dateText}}</p>\n" +
    "                </div>\n" +
    "                <div class=\"visible-xs\">\n" +
    "                    <br>\n" +
    "                    <h3 class=\"media-heading text-center\">{{post.title}}</h3>\n" +
    "                    <p data-ng-if=\"post.description\">{{post.description}}</p>\n" +
    "                    <p class=\"text-info small\">by {{post.authors}} on {{post.dateText}}</p>\n" +
    "                </div>\n" +
    "            </div>\n" +
    "            <hr>\n" +
    "        </a>\n" +
    "    </li>\n" +
    "</ul>");
}]);

    //  Blog Module
    //  ===============
    //
    //  Simple blog pagination directives and code highlight with highlight.js
    angular.module('lux.blog', ['lux.page', 'templates-blog', 'highlight'])
        .value('blogDefaults', {
            centerMath: true,
            fallback: true
        })
        //
        .controller('BlogEntry', ['$scope', 'pageService', '$lux', function ($scope, pageService, $lux) {
            var post = $scope.post;
            if (!post)
                $lux.log.error('post not available in $scope, cannot use pagination controller!');
            else {
                if (!post.date)
                    post.date = post.published || post.last_modified;
                pageService.addInfo(post, $scope);
            }
        }])
        //
        .directive('blogPagination', function () {
            return {
                templateUrl: "blog/pagination.tpl.html",
                restrict: 'AE'
            };
        })
        //
        .directive('blogHeader', function () {
            return {
                templateUrl: "blog/header.tpl.html",
                restrict: 'AE'
            };
        })
        //
        .directive('katex', ['blogDefaults', function (blogDefaults) {

            function error (element, err) {
                element.html("<div class='alert alert-danger' role='alert'>" + err + "</div>");
            }

            function render(katex, text, element) {
                try {
                    katex.render(text, element[0]);
                }
                catch(err) {
                    if (blogDefaults.fallback) {
                        require(['mathjax'], function (mathjax) {
                            try {
                                if (text.substring(0, 15) === '\\displaystyle {')
                                    text = text.substring(15, text.length-1);
                                element.append(text);
                                mathjax.Hub.Queue(["Typeset", mathjax.Hub, element[0]]);
                            } catch (e) {
                                error(element, err += ' - ' + e);
                            }
                        });
                    } else
                        error(element, err);
                }
            }

            return {
                restrict: 'AE',

                link: function (scope, element, attrs) {
                    var text = element.html();
                    if (element[0].tagName === 'DIV') {
                        if (blogDefaults.centerMath)
                            element.addClass('text-center');
                        text = '\\displaystyle {' + text + '}';
                        element.addClass('katex-outer');
                    }
                    if (typeof(katex) === 'undefined')
                        require(['katex'], function (katex) {
                            render(katex, text, element);
                        });
                    else
                        render(katex, text, element);
                }
            };
        }]);

    //
    //  Code highlighting with highlight.js
    //
    //  This module is added to the blog module so that the highlight
    //  directive can be used. Alternatively, include the module in the
    //  module to be bootstrapped.
    //
    //  Note:
    //      MAKE SURE THE lux.extensions.code EXTENSIONS IS INCLUDED IN
    //      YOUR CONFIG FILE
    angular.module('highlight', [])
        .directive('highlight', ['$rootScope', '$log', function ($rootScope, log) {
            return {
                link: function link(scope, element, attrs) {
                    log.info('Highlighting code');
                    highlight(element);
                }
            };
        }]);

    var highlight = function (elem) {
        require(['highlight'], function () {
            forEach($(elem)[0].querySelectorAll('code'), function(block) {
                var elem = $(block),
                    parent = elem.parent();
                if (isTag(parent, 'pre')) {
                    root.hljs.highlightBlock(block);
                    parent.addClass('hljs');
                } else {
                    elem.addClass('hljs inline');
                }
            });
            // Handle sphinx highlight
            forEach($(elem)[0].querySelectorAll('.highlight pre'), function(block) {
                var elem = $(block).addClass('hljs'),
                    div = elem.parent(),
                    p = div.parent();
                if (p.length && p[0].className.substring(0, 10) === 'highlight-')
                    div[0].className = 'language-' + p[0].className.substring(10);
                root.hljs.highlightBlock(block);
            });

        });
    };


    angular.module('lux.bs', ['mgcrea.ngStrap', 'templates-bs'])

        .config(['$tooltipProvider', function($tooltipProvider) {

            extend($tooltipProvider.defaults, {
                template: "bs/tooltip.tpl.html"
            });
        }]);
angular.module('templates-bs', ['bs/tooltip.tpl.html']);

angular.module("bs/tooltip.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("bs/tooltip.tpl.html",
    "<div class=\"tooltip in\" ng-show=\"title\">\n" +
    "    <div class=\"tooltip-arrow\"></div>\n" +
    "    <div class=\"tooltip-inner\" ng-bind=\"title\"></div>\n" +
    "</div>");
}]);

angular.module('templates-nav', ['nav/link.tpl.html', 'nav/navbar.tpl.html', 'nav/navbar2.tpl.html']);

angular.module("nav/link.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("nav/link.tpl.html",
    "<a ng-if=\"link.title\" ng-href=\"{{link.href}}\" data-title=\"{{link.title}}\" ng-click=\"clickLink($event, link)\"\n" +
    "ng-attr-target=\"{{link.target}}\" bs-tooltip=\"tooltip\">\n" +
    "<i ng-if=\"link.icon\" class=\"{{link.icon}}\"></i> {{link.name}}</a>\n" +
    "<a ng-if=\"!link.title\" ng-href=\"{{link.href}}\" ng-attr-target=\"{{link.target}}\">\n" +
    "<i ng-if=\"link.icon\" class=\"{{link.icon}}\"></i> {{link.name}}</a>");
}]);

angular.module("nav/navbar.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("nav/navbar.tpl.html",
    "<nav ng-attr-id=\"{{navbar.id}}\" class=\"navbar navbar-{{navbar.themeTop}}\"\n" +
    "ng-class=\"{'navbar-fixed-top':navbar.fixed, 'navbar-static-top':navbar.top}\" role=\"navigation\"\n" +
    "ng-model=\"navbar.collapse\" bs-collapse>\n" +
    "    <div class=\"{{navbar.container}}\">\n" +
    "        <div class=\"navbar-header\">\n" +
    "            <button ng-if=\"navbar.toggle\" type=\"button\" class=\"navbar-toggle\" bs-collapse-toggle>\n" +
    "                <span class=\"sr-only\">Toggle navigation</span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "            </button>\n" +
    "            <a ng-if=\"navbar.brandImage\" href=\"{{navbar.url}}\" class=\"navbar-brand\" target=\"{{navbar.target}}\">\n" +
    "                <img ng-src=\"{{navbar.brandImage}}\" alt=\"{{navbar.brand || 'brand'}}\">\n" +
    "            </a>\n" +
    "            <a ng-if=\"!navbar.brandImage && navbar.brand\" href=\"{{navbar.url}}\" class=\"navbar-brand\" target=\"{{navbar.target}}\">\n" +
    "                {{navbar.brand}}\n" +
    "            </a>\n" +
    "        </div>\n" +
    "        <div class=\"navbar-collapse\" bs-collapse-target>\n" +
    "            <ul ng-if=\"navbar.items\" class=\"nav navbar-nav\">\n" +
    "                <li ng-repeat=\"link in navbar.items\" ng-class=\"{active:activeLink(link)}\" navbar-link>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "            <ul ng-if=\"navbar.itemsRight\" class=\"nav navbar-nav navbar-right\">\n" +
    "                <li ng-repeat=\"link in navbar.itemsRight\" ng-class=\"{active:activeLink(link)}\" navbar-link>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</nav>");
}]);

angular.module("nav/navbar2.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("nav/navbar2.tpl.html",
    "<nav class=\"navbar navbar-{{navbar.themeTop}} navbar-fixed-top navbar-static-top\" role=\"navigation\" ng-model=\"navbar.collapse\" bs-collapse>\n" +
    "    <div class=\"navbar-header\">\n" +
    "        <button ng-if=\"navbar.toggle\" type=\"button\" class=\"navbar-toggle\" bs-collapse-toggle>\n" +
    "            <span class=\"sr-only\">Toggle navigation</span>\n" +
    "            <span class=\"icon-bar\"></span>\n" +
    "            <span class=\"icon-bar\"></span>\n" +
    "            <span class=\"icon-bar\"></span>\n" +
    "        </button>\n" +
    "        <a ng-if=\"navbar.brandImage\" href=\"{{navbar.url}}\" class=\"navbar-brand\" target=\"{{navbar.target}}\">\n" +
    "            <img ng-src=\"{{navbar.brandImage}}\" alt=\"{{navbar.brand || 'brand'}}\">\n" +
    "        </a>\n" +
    "        <a ng-if=\"!navbar.brandImage && navbar.brand\" href=\"{{navbar.url}}\" class=\"navbar-brand\" target=\"{{navbar.target}}\">\n" +
    "            {{navbar.brand}}\n" +
    "        </a>\n" +
    "    </div>\n" +
    "    <ul class=\"nav navbar-nav navbar-right\">\n" +
    "        <li ng-repeat=\"item in navbar.items\">\n" +
    "            <a href=\"{{item.href}}\" target=\"{{item.target}}\" title=\"{{item.title || item.label || item.value}}\">\n" +
    "            <i ng-if=\"item.icon\" class=\"{{item.icon}}\"></i> {{item.label || item.value}}</a>\n" +
    "        </li>\n" +
    "    </ul>\n" +
    "    <div class=\"sidebar navbar-{{navbar.theme}}\" role=\"navigation\">\n" +
    "        <div class=\"sidebar-nav sidebar-collapse\" bs-collapse-target>\n" +
    "            <ul id=\"side-menu\" class=\"nav nav-side\">\n" +
    "                <li ng-if=\"navbar.search\" class=\"sidebar-search\">\n" +
    "                    <div class=\"input-group custom-search-form\">\n" +
    "                        <input class=\"form-control\" type=\"text\" placeholder=\"Search...\">\n" +
    "                        <span class=\"input-group-btn\">\n" +
    "                            <button class=\"btn btn-default\" type=\"button\" ng-click=\"search()\">\n" +
    "                                <i class=\"fa fa-search\"></i>\n" +
    "                            </button>\n" +
    "                        </span>\n" +
    "                    </div>\n" +
    "                </li>\n" +
    "                <li ng-repeat=\"link in navbar.items2\">\n" +
    "                    <a ng-if=\"!link.links\" href=\"{{link.href}}\">{{link.label || link.value || link.href}}</a>\n" +
    "                    <a ng-if=\"link.links\" href=\"{{link.href}}\" class=\"with-children\">{{link.label || link.value}}</a>\n" +
    "                    <a ng-if=\"link.links\" href=\"#\" class=\"pull-right toggle\" ng-click=\"togglePage($event)\">\n" +
    "                        <i class=\"fa\" ng-class=\"{'fa-chevron-left': !link.active, 'fa-chevron-down': link.active}\"></i></a>\n" +
    "                    <ul ng-if=\"link.links\" class=\"nav nav-second-level collapse\" ng-class=\"{in: link.active}\">\n" +
    "                        <li ng-repeat=\"link in link.links\">\n" +
    "                            <a ng-if=\"!link.vars\" href=\"{{link.href}}\" ng-click=\"loadPage($event)\">{{link.label || link.value}}</a>\n" +
    "                        </li>\n" +
    "                    </ul>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</nav>");
}]);


    //
    //  Lux Navigation module
    //
    //  * Requires "angular-strap" for the collapsable directives
    //
    //  Include this module to render bootstrap navigation templates
    //  The navigation should be available as the ``navbar`` object within
    //  the ``luxContext`` object:
    //
    //      luxContext.navbar = {
    //          items: [{href="/", value="Home"}]
    //      };
    //
    var navBarDefaults = {
        collapseWidth: 768,
        theme: 'default',
        search_text: '',
        collapse: '',
        // Navigation place on top of the page (add navbar-static-top class to navbar)
        // nabar2 it is always placed on top
        top: false,
        search: false,
        url: lux.context.url,
        target: '',
        toggle: true,
        fluid: true
    };

    angular.module('lux.nav', ['templates-nav', 'lux.services', 'lux.bs'])
        //
        .service('navService', ['$location', function ($location) {

            this.initScope = function (scope, opts) {
                var navbar = extend({}, navBarDefaults, getOptions(opts), scope.navbar);
                if (!navbar.url)
                    navbar.url = '/';
                if (!navbar.themeTop)
                    navbar.themeTop = navbar.theme;
                navbar.container = navbar.fluid ? 'container-fluid' : 'container';

                this.maybeCollapse(navbar);
                scope.activeLink = this.activeLink;
                scope.clickLink = function (e, link) {
                    if (link.click) {
                        var func = scope[link.click];
                        if (func)
                            func(e, link.href, link);
                    }
                };
                scope.navbar = navbar;
                return navbar;
            };

            this.maybeCollapse = function (navbar) {
                var width = window.innerWidth > 0 ? window.innerWidth : screen.width,
                    c = navbar.collapse;
                if (width < navbar.collapseWidth)
                    navbar.collapse = 'collapse';
                else
                    navbar.collapse = '';
                return c !== navbar.collapse;
            };

            // Check if a url is active
            this.activeLink = function (url) {
                var loc;
                if (url)
                    url = typeof(url) === 'string' ? url : url.href || url.url;
                if (isAbsolute.test(url))
                    loc = $location.absUrl();
                else
                    loc = $location.path();
                var rest = loc.substring(url.length),
                    base = loc.substring(0, url.length),
                    folder = url.substring(url.length-1) === '/';
                return base === url && (folder || (rest === '' || rest.substring(0, 1) === '/'));
            };
        }])
        //
        .directive('navbarLink', function () {
            return {
                templateUrl: "nav/link.tpl.html",
                restrict: 'A'
            };
        })
        //
        //  Directive for the simple navbar
        //  This directive does not require the Navigation controller
        .directive('navbar', ['navService', function (navService) {
            //
            return {
                templateUrl: "nav/navbar.tpl.html",
                restrict: 'AE',
                // Link function
                link: function (scope, element, attrs) {
                    navService.initScope(scope, attrs);
                    //
                    windowResize(function () {
                        if (navService.maybeCollapse(scope.navbar))
                            scope.$apply();
                    });
                    //
                    // When using ui-router, and a view changes collapse the
                    //  navigation if needed
                    scope.$on('$locationChangeSuccess', function () {
                        navService.maybeCollapse(scope.navbar);
                        //scope.$apply();
                    });
                }
            };
        }])
        //
        //  Directive for the navbar with sidebar (nivebar2 template)
        .directive('navbar2', ['navService', '$compile', function (navService, $compile) {
            return {
                restrict: 'AE',
                // We need to use the compile function so that we remove the
                // before it is included in the bootstraping algorithm
                compile: function compile(element) {
                    var inner = element.html(),
                        className = element[0].className;
                    //
                    element.html('');

                    return {
                        post: function (scope, element, attrs) {
                            scope.navbar2Content = inner;
                            navService.initScope(scope, attrs);

                            inner = $compile('<div data-nav-side-bar></div>')(scope);
                            element.replaceWith(inner.addClass(className));
                            //
                            windowResize(function () {
                                if (navService.maybeCollapse(scope.navbar))
                                    scope.$apply();
                            });
                        }
                    };
                }
            };
        }])
        //
        //  Directive for the navbar with sidebar (nivebar2 template)
        .directive('navSideBar', ['$compile', '$document', function ($compile, $document) {
            return {
                templateUrl: "nav/navbar2.tpl.html",

                restrict: 'A',

                link: function (scope, element, attrs) {
                    var navbar = scope.navbar;
                    element.addClass('navbar2-wrapper');
                    if (navbar && navbar.theme)
                        element.addClass('navbar-' + navbar.theme);
                    var inner = $($document[0].createElement('div')).addClass('navbar2-page')
                                    .append(scope.navbar2Content);
                    // compile
                    $compile(inner)(scope);
                    // and append
                    element.append(inner);
                    //
                    function resize() {
                        inner.attr('style', 'min-height: ' + windowHeight() + 'px');
                    }
                    //
                    windowResize(resize);
                    //
                    resize();
                }
            };
        }]);
    //
    //  Angular module for photos
    //  ============================
    //
    angular.module('photos', ['lux.services'])
        .directive('flickr', ['$lux', function ($lux) {
            //
            var endpoint = 'https://api.flickr.com/services/feeds/photos_faves.gne';
            //
            function display (data) {

            }
            //
            return {
                restrict: 'AE',
                //
                link: function (scope, element, attrs) {
                    var id = attrs.id;
                    $lux.http({
                        method: 'get',
                        data: {'id': id, format: 'json'}
                    }).success(function (data) {
                        display(data);
                    });
                }
            };
        }]);

    var
    //
    lorem_defaults = {
        paragraphs: 3,
        // number of words per paragraph
        words: null,
        ptags: true
    },
    //
    lorem_text = [
         "Nam quis nulla. Integer malesuada. In in enim a arcu imperdiet malesuada. Sed vel lectus. Donec odio urna, tempus molestie, porttitor ut, iaculis quis, sem. Phasellus rhoncus. Aenean id metus id velit ullamcorper pulvinar. Vestibulum fermentum tortor id mi. Pellentesque ipsum. Nulla non arcu lacinia neque faucibus fringilla. Nulla non lectus sed nisl molestie malesuada. Proin in tellus sit amet nibh dignissim sagittis. Vivamus luctus egestas leo. Maecenas sollicitudin. Nullam rhoncus aliquam metus. Etiam egestas wisi a erat.",
         "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Nullam feugiat, turpis at pulvinar vulputate, erat libero tristique tellus, nec bibendum odio risus sit amet ante. Aliquam erat volutpat. Nunc auctor. Mauris pretium quam et urna. Fusce nibh. Duis risus. Curabitur sagittis hendrerit ante. Aliquam erat volutpat. Vestibulum erat nulla, ullamcorper nec, rutrum non, nonummy ac, erat. Duis condimentum augue id magna semper rutrum. Nullam justo enim, consectetuer nec, ullamcorper ac, vestibulum in, elit. Proin pede metus, vulputate nec, fermentum fringilla, vehicula vitae, justo. Fusce consectetuer risus a nunc. Aliquam ornare wisi eu metus. Integer pellentesque quam vel velit. Duis pulvinar.",
         "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Morbi gravida libero nec velit. Morbi scelerisque luctus velit. Etiam dui sem, fermentum vitae, sagittis id, malesuada in, quam. Proin mattis lacinia justo. Vestibulum facilisis auctor urna. Aliquam in lorem sit amet leo accumsan lacinia. Integer rutrum, orci vestibulum ullamcorper ultricies, lacus quam ultricies odio, vitae placerat pede sem sit amet enim. Phasellus et lorem id felis nonummy placerat. Fusce dui leo, imperdiet in, aliquam sit amet, feugiat eu, orci. Aenean vel massa quis mauris vehicula lacinia. Quisque tincidunt scelerisque libero. Maecenas libero. Etiam dictum tincidunt diam. Donec ipsum massa, ullamcorper in, auctor et, scelerisque sed, est. Suspendisse nisl. Sed convallis magna eu sem. Cras pede libero, dapibus nec, pretium sit amet, tempor quis, urna.",
         "Etiam posuere quam ac quam. Maecenas aliquet accumsan leo. Nullam dapibus fermentum ipsum. Etiam quis quam. Integer lacinia. Nulla est. Nulla turpis magna, cursus sit amet, suscipit a, interdum id, felis. Integer vulputate sem a nibh rutrum consequat. Maecenas lorem. Pellentesque pretium lectus id turpis. Etiam sapien elit, consequat eget, tristique non, venenatis quis, ante. Fusce wisi. Phasellus faucibus molestie nisl. Fusce eget urna. Curabitur vitae diam non enim vestibulum interdum. Nulla quis diam. Ut tempus purus at lorem.",
         "In sem justo, commodo ut, suscipit at, pharetra vitae, orci. Duis sapien nunc, commodo et, interdum suscipit, sollicitudin et, dolor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Aliquam id dolor. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos hymenaeos. Mauris dictum facilisis augue. Fusce tellus. Pellentesque arcu. Maecenas fermentum, sem in pharetra pellentesque, velit turpis volutpat ante, in pharetra metus odio a lectus. Sed elit dui, pellentesque a, faucibus vel, interdum nec, diam. Mauris dolor felis, sagittis at, luctus sed, aliquam non, tellus. Etiam ligula pede, sagittis quis, interdum ultricies, scelerisque eu, urna. Nullam at arcu a est sollicitudin euismod. Praesent dapibus. Duis bibendum, lectus ut viverra rhoncus, dolor nunc faucibus libero, eget facilisis enim ipsum id lacus. Nam sed tellus id magna elementum tincidunt.",
         "Morbi a metus. Phasellus enim erat, vestibulum vel, aliquam a, posuere eu, velit. Nullam sapien sem, ornare ac, nonummy non, lobortis a, enim. Nunc tincidunt ante vitae massa. Duis ante orci, molestie vitae, vehicula venenatis, tincidunt ac, pede. Nulla accumsan, elit sit amet varius semper, nulla mauris mollis quam, tempor suscipit diam nulla vel leo. Etiam commodo dui eget wisi. Donec iaculis gravida nulla. Donec quis nibh at felis congue commodo. Etiam bibendum elit eget erat.",
         "Praesent in mauris eu tortor porttitor accumsan. Mauris suscipit, ligula sit amet pharetra semper, nibh ante cursus purus, vel sagittis velit mauris vel metus. Aenean fermentum risus id tortor. Integer imperdiet lectus quis justo. Integer tempor. Vivamus ac urna vel leo pretium faucibus. Mauris elementum mauris vitae tortor. In dapibus augue non sapien. Aliquam ante. Curabitur bibendum justo non orci.",
         "Morbi leo mi, nonummy eget, tristique non, rhoncus non, leo. Nullam faucibus mi quis velit. Integer in sapien. Fusce tellus odio, dapibus id, fermentum quis, suscipit id, erat. Fusce aliquam vestibulum ipsum. Aliquam erat volutpat. Pellentesque sapien. Cras elementum. Nulla pulvinar eleifend sem. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Quisque porta. Vivamus porttitor turpis ac leo.",
         "Maecenas ipsum velit, consectetuer eu, lobortis ut, dictum at, dui. In rutrum. Sed ac dolor sit amet purus malesuada congue. In laoreet, magna id viverra tincidunt, sem odio bibendum justo, vel imperdiet sapien wisi sed libero. Suspendisse sagittis ultrices augue. Mauris metus. Nunc dapibus tortor vel mi dapibus sollicitudin. Etiam posuere lacus quis dolor. Praesent id justo in neque elementum ultrices. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos hymenaeos. In convallis. Fusce suscipit libero eget elit. Praesent vitae arcu tempor neque lacinia pretium. Morbi imperdiet, mauris ac auctor dictum, nisl ligula egestas nulla, et sollicitudin sem purus in lacus.",
         "Aenean placerat. In vulputate urna eu arcu. Aliquam erat volutpat. Suspendisse potenti. Morbi mattis felis at nunc. Duis viverra diam non justo. In nisl. Nullam sit amet magna in magna gravida vehicula. Mauris tincidunt sem sed arcu. Nunc posuere. Nullam lectus justo, vulputate eget, mollis sed, tempor sed, magna. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Etiam neque. Curabitur ligula sapien, pulvinar a, vestibulum quis, facilisis vel, sapien. Nullam eget nisl. Donec vitae arcu."
    ];

    angular.module('lux.lorem', [])
        .directive('lorem', function () {
            //
            return {
                restrict: 'AE',
                //
                link: function (scope, element, attrs) {
                    var opts = extend({}, lorem_defaults, attrs),
                        howmany = +opts.paragraphs,
                        paragraphs = [],
                        ipsum_text = "";
                    //
                    for (var i = 0; i < howmany; i++){
                        paragraphs.push(lorem_text[Math.floor(Math.random()*lorem_text.length)]);
                    }
                    if (opts.words) {
                        var numOfWords = +opts.words,
                            oldparagraphs = paragraphs;
                        paragraphs = [];
                        oldparagraphs.forEach(function (paragraph) {
                            var words = paragraph.split( ' ' ).splice(0, numOfWords);
                            paragraphs.push(words.join(' '));
                        });
                    }
                    paragraphs.forEach(function (paragraph) {
                        if (opts.tags)
                            element.append($('<p>'+paragraph+'</p>'));
                        else
                            element.append(paragraph+'\n\n');
                    });
                }
            };
        });


    //  Google Spreadsheet API
    //  -----------------------------
    //
    //  Create one by passing the key of the spreadsheeet containing data
    //
    //      var api = $lux.api({name: 'googlesheets', url: sheetkey});
    //

    //
    //
    var GoogleModel = function ($lux, data, opts) {
        var i, j, ilen, jlen;
        this.column_names = [];
        this.name = data.feed.title.$t;
        this.elements = [];
        this.raw = data; // A copy of the sheet's raw data, for accessing minutiae

        if (typeof(data.feed.entry) === 'undefined') {
            $lux.log.warn("Missing data for " + this.name + ", make sure you didn't forget column headers");
            return;
        }

        $lux.log.info('Building models from google sheet');

        for (var key in data.feed.entry[0]) {
            if (/^gsx/.test(key)) this.column_names.push(key.replace("gsx$", ""));
        }

        for (i = 0, ilen = data.feed.entry.length; i < ilen; i++) {
            var source = data.feed.entry[i];
            var element = {};
            for (j = 0, jlen = this.column_names.length; j < jlen; j++) {
                var cell = source["gsx$" + this.column_names[j]];
                if (typeof(cell) !== 'undefined') {
                    if (cell.$t !== '' && !isNaN(cell.$t))
                        element[this.column_names[j]] = +cell.$t;
                    else
                        element[this.column_names[j]] = cell.$t;
                } else {
                    element[this.column_names[j]] = '';
                }
            }
            if (element.rowNumber === undefined)
                element.rowNumber = i + 1;
            this.elements.push(element);
        }
    };

    var GoogleSeries = function ($lux, data, opts) {
        var i, j, ilen, jlen;
        this.column_names = [];
        this.name = data.feed.title.$t;
        this.series = [];
        this.raw = data; // A copy of the sheet's raw data, for accessing minutiae

        if (typeof(data.feed.entry) === 'undefined') {
            $lux.log.warn("Missing data for " + this.name + ", make sure you didn't forget column headers");
            return;
        }
        $lux.log.info('Building series from google sheet');

        for (var key in data.feed.entry[0]) {
            if (/^gsx/.test(key)) {
                var name = key.replace("gsx$", "");
                this.column_names.push(name);
                this.series.push([name]);
            }
        }

        for (i = 0, ilen = data.feed.entry.length; i < ilen; i++) {
            var source = data.feed.entry[i];
            for (j = 0, jlen = this.column_names.length; j < jlen; j++) {
                var cell = source["gsx$" + this.column_names[j]],
                    serie = this.series[j];
                if (typeof(cell) !== 'undefined') {
                    if (cell.$t !== '' && !isNaN(cell.$t))
                        serie.push(+cell.$t);
                    else
                        serie.push(cell.$t);
                } else {
                    serie.push('');
                }
            }
        }
    };

    //
    //  Module for interacting with google API and services
    angular.module('lux.google', ['lux.api'])
        //
        .run(['$rootScope', '$lux', '$log', '$location', function (scope, $lux, log, location) {
            var analytics = scope.google ? scope.google.analytics : null;

            if (analytics && analytics.id) {
                var ga = analytics.ga || 'ga';
                if (typeof ga === 'string')
                    ga = root[ga];
                log.info('Register events for google analytics ' + analytics.id);
                scope.$on('$stateChangeSuccess', function (event, toState, toParams, fromState, fromParams) {
                    var state = scope.$state;
                    //
                    if (state) {
                        var fromHref = stateHref(state, fromState, fromParams),
                            toHref = stateHref(state, toState, toParams);
                        if (fromHref !== 'null') {
                            if (fromHref !== toHref)
                                ga('send', 'pageview', {page: toHref});
                            else
                                ga('send', 'event', 'stateChange', toHref);
                            ga('send', 'event', 'fromState', fromHref, toHref);
                        }
                    }
                });
            }

            // Googlesheet api
            $lux.registerApi('googlesheets', {
                //
                endpoint: "https://spreadsheets.google.com",
                //
                url: function (urlparams) {
                    // when given the url is of the form key/worksheet where
                    // key is the key of the spreadsheet you want to retrieve,
                    // worksheet is the positional or unique identifier of the worksheet
                    if (this._url) {
                        if (urlparams) {
                            return this.endpoint + '/feeds/list/' + this._url + '/' + urlparams.id + '/public/values?alt=json';
                        } else {
                            return null;
                        }
                    }
                },
                //
                getList: function (options) {
                    var Model = this.Model,
                        opts = this.options,
                        $lux = this.$lux;
                    return this.request('GET', null, options).then(function (response) {
                        return response;
                    });
                },
                //
                get: function (urlparams, options) {
                    var Model = this.Model,
                        opts = this.options,
                        $lux = this.$lux;
                    return this.request('GET', urlparams, options).then(function (response) {
                        response.data = opts.orientation === 'columns' ? new GoogleSeries(
                            $lux, response.data) : new GoogleModel($lux, response.data);
                        return response;
                    });
                }
            });

        }])
        //
        .directive('googleMap', function () {
            return {
                //
                // Create via element tag
                // <d3-force data-width=300 data-height=200></d3-force>
                restrict: 'AE',
                //
                link: function (scope, element, attrs) {
                    require(['google-maps'], function () {
                        on_google_map_loaded(function () {
                            var lat = +attrs.lat,
                                lng = +attrs.lng,
                                loc = new google.maps.LatLng(lat, lng),
                                opts = {
                                    center: loc,
                                    zoom: attrs.zoom ? +attrs.zoom : 8
                                },
                                map = new google.maps.Map(element[0], opts);
                            var marker = new google.maps.Marker({
                                position: loc,
                                map: map,
                                title: attrs.marker
                            });
                            //
                            windowResize(function () {
                                google.maps.event.trigger(map, 'resize');
                                map.setCenter(loc);
                                map.setZoom(map.getZoom());
                            }, 500);
                        });
                    });
                }
            };
        });

    lux.d3Directive = function (name, VizClass, moduleName) {

        moduleName = moduleName || 'd3viz';

        var dname = 'viz' + name.substring(0,1).toUpperCase() + name.substring(1);

        function loadData ($lux) {

            return function (callback) {
                var self = this,
                    src = this.attrs.src;
                if (typeof src === 'object') {
                    var id = src.id,
                        api = $lux.api(src);
                    if (api) {
                        var p = id ? api.get(id) : api.getList();
                        p.then(function (response) {
                            self.setData(response.data, callback);
                            return response;
                        });
                    }
                } else if (src) {
                    d3.json(src, function(error, json) {
                        if (!error) {
                            self.setData(json, callback);
                            return self.attrs.data;
                        }
                    });
                }
            };
        }

        // Obtain extra information from javascript objects
        function getOptions(d3, attrs) {
            if (typeof attrs.options === 'string') {
                var obj = root,
                    bits= attrs.options.split('.');

                for (var i=0; i<bits.length; ++i) {
                    obj = obj[bits[i]];
                    if (!obj) break;
                }
                if (typeof obj === 'function')
                    obj = obj(d3, attrs);
                attrs = extend(attrs, obj);
            }
            return attrs;
        }

        angular.module(moduleName)
            .directive(dname, ['$lux', function ($lux) {
                return {
                        //
                        // Create via element tag or attribute
                        restrict: 'AE',
                        //
                        link: function (scope, element, attrs) {
                            var viz = element.data(dname);
                            if (!viz) {
                                var options = getOptions(d3, attrs),
                                    autoBuild = options.autoBuild;
                                options.autoBuild = false;
                                // add scope to the options
                                options.scope = scope;
                                viz = new VizClass(element[0], options);
                                element.data(viz);
                                viz.loadData = loadData($lux);
                                if (autoBuild === undefined || autoBuild)
                                    viz.build();
                            }
                        }
                    };
            }]);
    };
    //
    // Load d3 extensions into angular 'd3viz' module
    //  d3ext is the d3 extension object
    //  name is the optional module name for angular (default to d3viz)
    lux.addD3ext = function (d3) {
        //
        var moduleName = 'd3viz';

        // Loop through d3 extensions and create directives
        // for each Visualization class
        angular.forEach(d3.ext, function (VizClass, name) {
            if (d3.ext.isviz(VizClass)) {
                lux.d3Directive(name, VizClass, moduleName);
            }
        });

        return lux;
    };

    angular.module('d3viz', ['lux.services'])
        .directive('jstats', function () {
            return {
                link: function (scope, element, attrs) {
                    var mode = attrs.mode ? +attrs.mode : 1;
                    require(rcfg.min(['stats']), function () {
                        var stats = new Stats();
                        stats.setMode(mode);
                        scope.stats = stats;
                        element.append($(stats.domElement));
                    });
                }
            };
        });

    angular.module('lux.services', ['lux.api', 'lux.web.api', 'lux.static.api']);

	return lux;
}));