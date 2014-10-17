//      Lux Library - v0.1.0

//      Compiled 2014-10-17.
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
        define(['angular'], function (angular) {
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

    var lux = {version: '0.1.0'},
        ready_callbacks = [],
        forEach = angular.forEach,
        extend = angular.extend,
        angular_bootstrapped = false,
        isArray = angular.isArray,
        isString = angular.isString,
        $ = angular.element,
        slice = Array.prototype.slice,
        defaults = {
            url: '',    // base url for the web site
            media: '',  // default url for media content
            html5mode: true, //  html5mode for angular
            hashPrefix: '!'
        };
    //
    lux.$ = $;
    lux.forEach = angular.forEach;
    lux.context = extend({}, defaults, root.luxContext);

    // Callbacks run after angular has finished bootstrapping
    lux.add_ready_callback = function (callback) {
        if (ready_callbacks === true) callback();
        else ready_callbacks.push(callback);
    };

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

    var
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
    //  getOPtions
    //  ===============
    //
    //  Retrive options for the ``options`` string in ``attrs`` if available.
    //  Used by directive when needing to specify options in javascript rather
    //  than html data attributes.
    getOptions = function (attrs) {
        if (attrs && typeof attrs.options === 'string') {
            var obj = root,
                bits= attrs.options.split('.');

            for (var i=0; i<bits.length; ++i) {
                obj = obj[bits[i]];
                if (!obj) break;
            }
            if (typeof obj === 'function')
                obj = obj();
            delete attrs.options;
            attrs = extend(attrs, obj);
        }
        var options = {};
        forEach(attrs, function (value, name) {
            if (name.substring(0, 1) !== '$')
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
    //
    // Object containing apis by name
    var ApiTypes = lux.ApiTypes = {};
    //
    // If CSRF token is not available
    // try to obtain it from the meta tags
    //if (!context.csrf) {
    //    var name = $("meta[name=csrf-param]").attr('content'),
    //        token = $("meta[name=csrf-token]").attr('content');
    //    if (name && token) {
    //        context.csrf = {};
    //        context.csrf[name] = token;
    //    }
    //}
    //
    //  Lux Api service factory for angular
    //  ---------------------------------------
    angular.module('lux.services', [])
        .service('$lux', ['$location', '$q', '$http', '$log', '$timeout',
                function ($location, $q, $http, $log, $timeout) {
            var $lux = this;

            this.location = $location;
            this.log = $log;
            this.http = $http;
            this.q = $q;
            this.timeout = $timeout;

            // A post method with CSRF parameter
            this.post = function (url, data, cfg) {
                if (lux.context.csrf) {
                    data || (data = {});
                    angular.extend(data, lux.context.csrf);
                }
                return $http.post(url, data, cfg);
            };

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
                else
                    return new Api(context.name, context.url, context.options, $lux);
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
            if (urlparams)
                return self._url + '/' + urlparams.id;
            else
                return self._url;
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
        //  Execute an API call for a given request
        //  This method is hardly used directly, the ``request`` method is normally used.
        //
        //      request: a request object obtained from the ``request`` method
        call: function (request) {
            var $lux = this.$lux;
            //
            if (!this._url && ! this.name) {
                return request.error('api should have url or name');
            }

            if (!this._url) {
                if (this.apiUrls) {
                    this._url = this.apiUrls[this.name] || this.apiUrls[this.name + '_url'];
                    //
                    // No api url!
                    if (!this.url)
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
    //
    lux.createApi = function (name, object) {
        //
        ApiTypes[name] = ApiClient.extend(object);
        //
        return ApiTypes[name];
    };

    //
    //  Lux Default API
    //  ----------------------
    //
    lux.createApi('lux', {
        //
        authentication: function (request) {
            var self = this;
            //
            if (lux.context.user) {
                $lux.log.info('Fetching authentication token');
                //
                $lux.post('/_token').success(function (data) {
                    self.auth = {user_token: data.token};
                    self.call(request);
                }).error(request.error);
                //
                return request.deferred.promise;
            } else {
                self.auth = {};
                self.call(request);
            }
        },
        //
        addAuth: function (api, options) {
            //
                    // Add authentication token
            if (this.user_token) {
                var headers = options.headers;
                if (!headers)
                    options.headers = headers = {};

                headers.Authorization = 'Bearer ' + this.user_token;
            }
        }
    });
    //
    //  Hash scrolling service
    angular.module('lux.scroll', [])
        //
        .run(['$rootScope', function (scope) {
            scope.scroll = extend({
                time: 1,
                offset: 0,
                frames: 25
            }, scope.scroll);
        }])
        //
        .service('scroll', ['$rootScope', '$location', '$log', '$timeout', function (scope, $location, log, timer) {
            //  ScrollToHash
            var targetClass = 'scroll-target',
                targetClassFinish = 'finished',
                luxScroll = scope.scroll,
                target = null;
            //
            this.toHash = function (hash, offset, delay) {
                var e;
                if (target || !hash)
                    return;
                if (hash.e) {
                    e = hash.e;
                    hash = hash.hash;
                }
                // set the location.hash to the id of
                // the element you wish to scroll to.
                if (typeof(hash) === 'string') {
                    if (hash.substring(0, 1) === '#')
                        hash = hash.substring(1);
                    target = document.getElementById(hash);
                    if (target) {
                        _clearTargets();
                        target = $(target).addClass(targetClass).removeClass(targetClassFinish);
                        if (e) {
                            e.preventDefault();
                            e.stopPropagation();
                        }
                        log.info('Scrolling to target #' + hash);
                        _scrollTo(offset || luxScroll.offset, delay);
                        return target;
                    }
                }
            };

            function _clearTargets () {
                forEach(document.querySelectorAll('.' + targetClass), function (el) {
                    $(el).removeClass(targetClass);
                });
            }

            function _scrollTo (offset, delay) {
                var i,
                    startY = currentYPosition(),
                    stopY = elmYPosition(target[0]) - offset,
                    distance = stopY > startY ? stopY - startY : startY - stopY;
                var step = Math.round(distance / luxScroll.frames),
                    y = startY;
                if (delay === null || delay === undefined) {
                    delay = 1000*luxScroll.time/luxScroll.frames;
                    if (distance < 200)
                        delay = 0;
                }
                _nextScroll(startY, delay, step, stopY);
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
                        $location.hash(target.attr('id'));
                        target.addClass(targetClassFinish);
                        target = null;
                    }
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

        }])
        //
        // Directive for adding smooth scrolling to hash links
        .directive('hashScroll', ['$log', '$location', 'scroll', function (log, location, scroll) {
            var innerTags = ['IMG', 'I', 'SPAN', 'TT'];
            //
            return {
                link: function (scope, element, attrs) {
                    //
                    log.info('Apply smooth scrolling');
                    scope.location = location;
                    scope.$watch('location.hash()', function(hash) {
                        // Hash change (when a new page is loaded)
                        scroll.toHash(hash, null, 0);
                    });
                    //
                    element.bind('click', function (e) {
                        var target = e.target;
                        while (target && innerTags.indexOf(target.tagName) > -1)
                            target = target.parentElement;
                        if (target && target.hash) {
                            scroll.toHash({hash: target.hash, e: e});
                        }
                    });
                }
            };
        }]);
    //
    //  Lux Static JSON API
    //  ------------------------
    //
    //  Api used by static sites
    lux.createApi('static', {
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
        }
    });
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

    function addPageInfo(page, $scope, dateFilter, $lux) {
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
    }

    //  Lux angular
    //  ==============
    //  Lux main module for angular. Design to work with the ``lux.extension.angular``
    angular.module('lux.page', ['lux.services', 'lux.form', 'lux.scroll', 'templates-page'])
        //
        .controller('Page', ['$scope', '$log', '$lux', 'dateFilter', function ($scope, log, $lux, dateFilter) {
            //
            $lux.log.info('Setting up angular page');
            //
            var page = $scope.page;
            // If the page is a string, retrieve it from the pages object
            if (typeof page === 'string')
                page = $scope.pages ? $scope.pages[page] : null;
            $scope.page = addPageInfo(page || {}, $scope, dateFilter, $lux);
            //
            // logout via post method
            $scope.logout = function(e, url) {
                e.preventDefault();
                e.stopPropagation();
                $lux.post(url).success(function (data) {
                    if (data.redirect)
                        window.location.replace(data.redirect);
                });
            };

            // Dismiss a message
            $scope.dismiss = function (m) {
                $lux.post('/_dismiss_message', {message: m});
            };

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
    var stateHref = function (state, State, Params) {
        var url = state.href(State);
        if (Params) {
            var n = url.length,
                url2 = state.href(State, Params);
            url = encodeURIComponent(url) + url2.substring(n);
            url = decodeURIComponent(url);
        }
        return url;
    };

    angular.module('lux.ui.router', ['lux.page', 'ui.router'])
        //
        .run(['$rootScope', '$state', '$stateParams', function (scope, $state, $stateParams) {
            //
            // It's very handy to add references to $state and $stateParams to the $rootScope
            scope.$state = $state;
            scope.$stateParams = $stateParams;
        }])
        .config(['$locationProvider', '$stateProvider', '$urlRouterProvider',
            function ($locationProvider, $stateProvider, $urlRouterProvider) {

            var
            hrefs = lux.context.hrefs,
            pages = lux.context.pages,
            state_config = function (page) {
                return {
                    url: page.url,
                    //
                    views: {
                        main: {
                            template: page.template,
                            //
                            resolve: {
                                // Fetch page information
                                page: ['$lux', '$stateParams', function ($lux, $stateParams) {
                                    if (page.api) {
                                        var api = $lux.api(page.api);
                                        if (api)
                                            return api.get($stateParams);
                                    }
                                }],
                                // Fetch items if needed
                                items: ['$lux', function ($lux) {
                                    if (page.apiItems) {
                                        var api = $lux.api(page.apiItems);
                                        if (api)
                                            return api.getList();
                                    }
                                }],
                            },
                            //
                            controller: page.controller
                        }
                    }
                };
            };

            $locationProvider.html5Mode(lux.context.html5mode).hashPrefix(lux.context.hashPrefix);
            //
            forEach(hrefs, function (href) {
                var page = pages[href];
                if (page.target !== '_self') {
                    var name = page.name;
                    if (!name) {
                        name = 'home';
                    }
                    $stateProvider.state(name, state_config(page));
                }
            });
        }])
        .controller('Html5', ['$scope', '$state', 'dateFilter', '$lux', 'page', 'items',
            function ($scope, $state, dateFilter, $lux, page, items) {
                if (page && page.status === 200) {
                    $scope.items = items ? items.data : null;
                    $scope.page = addPageInfo(page.data, $scope, dateFilter, $lux);
                }
            }])
        //
        .directive('dynamicPage', ['$compile', '$log', function ($compile, log) {
            return {
                link: function (scope, element, attrs) {
                    scope.$on('$stateChangeSuccess', function () {
                        var page = scope.page;
                        if (page.html && page.html.main) {
                            element.html(page.html.main);
                            log.info('Compiling new html content');
                            $compile(element.contents())(scope);
                        }
                    });
                }
            };
        }]);

    var FORMKEY = 'm__form',
        formDefaults = {};
    //
    // Change the form data depending on content type
    function formData(ct) {

        return function (data, getHeaders ) {
            angular.extend(data, lux.context.csrf);
            if (ct === 'application/x-www-form-urlencoded')
                return $.param(data);
            else if (ct === 'multipart/form-data') {
                var fd = new FormData();
                angular.forEach(data, function (value, key) {
                    fd.append(key, value);
                });
                return fd;
            } else {
                return data;
            }
        };
    }

    // A general from controller factory
    var formController = lux.formController = function ($scope, $lux, model) {
        model || (model = {});

        var page = $scope.$parent ? $scope.$parent.page : {};

        if (model)
            $scope.formModel = model.data || model;
        $scope.formClasses = {};
        $scope.formErrors = {};
        $scope.formMessages = {};

        if ($scope.formModel.name) {
            page.title = 'Update ' + $scope.formModel.name;
        }

        function formMessages (messages) {
            angular.forEach(messages, function (messages, field) {
                $scope.formMessages[field] = messages;
            });
        }

        // display field errors
        $scope.showErrors = function () {
            var error = $scope.form.$error;
            angular.forEach(error.required, function (e) {
                $scope.formClasses[e.$name] = 'has-error';
            });
        };

        // process form
        $scope.processForm = function($event) {
            $event.preventDefault();
            $event.stopPropagation();
            var $element = angular.element($event.target),
                apiname = $element.attr('data-api'),
                target = $element.attr('action'),
                promise,
                api;
            //
            if ($scope.form.$invalid) {
                return $scope.showErrors();
            }

            // Get the api information
            if (!target && apiname) {
                api = $lux.api(apiname);
                if (!api)
                    $lux.log.error('Could not find api url for ' + apiname);
            }

            $scope.formMessages = {};
            //
            if (target) {
                var enctype = $element.attr('enctype') || '',
                    ct = enctype.split(';')[0],
                    options = {
                        url: target,
                        method: $element.attr('method') || 'POST',
                        data: $scope.formModel,
                        transformRequest: formData(ct),
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
                    angular.forEach(data.messages, function (messages, field) {
                        $scope.formMessages[field] = messages;
                    });
                } else if (api) {
                    // Created
                    if (status === 201) {
                        $scope.formMessages[FORMKEY] = [{message: 'Succesfully created'}];
                    } else {
                        $scope.formMessages[FORMKEY] = [{message: 'Succesfully updated'}];
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
                        messages[FORMKEY] = [{message: msg, error: true}];
                    }
                } else {
                    status = status || 501;
                    msg = 'Server error (' + data.status + ')';
                    messages = {};
                    messages[FORMKEY] = [{message: msg, error: true}];
                }
                formMessages(messages);
            });
        };
    };

    var input_attributes = ['id', 'class', 'form', 'max', 'maxlength',
                            'min', 'name', 'placeholder', 'readonly',
                            'required', 'style', 'title', 'type', 'value'],
        form_attributes = ['id', 'class', 'style', 'title',
                           'action', 'enctype', 'name', 'novalidate'],
        global_attributes = ['id', 'class', 'style', 'title'],
        form_inputs = ['button', 'checkbox', 'color', 'date', 'datetime',
                       'datetime-local', 'email', 'file', 'hidden', 'image',
                       'month', 'number', 'password', 'radio', 'range',
                       'reset', 'search', 'submit', 'tel', 'text', 'time',
                       'url', 'week'];


    // Default form module for lux
    angular.module('lux.form', ['lux.services'])
        .value('elementAttributes', function (type) {
            if (form_inputs.indexOf(type) > -1)
                return input_attributes;
            else if (type === 'form')
                return form_attributes;
            else
                return global_attributes;
        })
        //
        // The formService is a reusable component for redering form fields
        .service('formService', ['$compile', '$log', 'elementAttributes',
                function ($compile, log, elementAttributes) {

            var radioTemplate = '<label>'+
                                '<input ng-class="field.class" ng-model="form[field.name]" id="{{field.id}}" name="{{field.name}}">'+
                                ' {{field.label}}</label>',
                inputTemplate = '<div class="form-group">'+
                                '<label for="{{field.id}}"> {{field.label}}</label>'+
                                '<input ng-class="field.class" ng-model="form[field.name]" id="{{field.id}}" name="{{field.name}}">'+
                                '</div>',
                fieldsetTemplate = '<fieldset><legend ng-if="field.legend">{{field.legend}}</legend></fieldset>';

            function fillDefaults (scope) {
                var field = scope.field;
                field.label = field.label || field.name;
                scope.formParameters[field.name] = 'form.' + field.name;
                scope.count++;
                if (!field.id)
                    field.id = field.name + '-' + scope.formid + '-' + scope.count;
            }

            // add attributes ``attrs`` to ``element``
            this.attrs = function (scope, element) {
                var attributes = elementAttributes(scope.field.type);
                forEach(scope.field, function (value, name) {
                    if (attributes.indexOf(name) > -1)
                        element.attr(name, value);
                });
                return element;
            };

            // Clear parent attributes
            this.removeAttrs = function (scope, element) {
                var attributes = elementAttributes(scope.type);
                forEach(attributes, function (name) {
                    delete scope[name];
                });
            };

            // Compile a form element with a scope
            this.compile = function (scope, element) {
                var self = this,
                    attributes = elementAttributes(scope.field.type);


                forEach(scope.children, function (child) {

                    if (child.field) {

                        var childScope = scope.$new(),
                            fieldCompiler = self[child.field.type];

                        // extend child.field with options
                        forEach(scope.field, function (value, name) {
                            if (attributes.indexOf(name) === -1 && child.field[name] === undefined)
                                child.field[name] = value;
                        });

                        if (!fieldCompiler)
                            fieldCompiler = self.input;

                        // extend child scope options with values form child attributes
                        element.append(fieldCompiler.call(self, extend(childScope, child)));
                    } else {
                        log.error('form child without field');
                    }
                });

                return this.attrs(scope, element);
            };

            // Compile a fieldset and its children
            this.fieldset = function (scope) {
                var element = $compile(fieldsetTemplate)(scope);
                return this.compile(scope, element);
            };

            this.radio = function (scope) {
                fillDefaults(scope);
                return this.attrs(scope, $compile(radioTemplate)(scope));
            };
            this.checkbox = this.radio;

            this.input = function (scope) {
                fillDefaults(scope);
                if (!scope.field.class)
                    scope.field.class = 'form-control';
                return $compile(inputTemplate)(scope);
                //return this.attrs(scope, $compile(inputTemplate)(scope));
            };

            this.button = function (scope) {
                var field = scope.field;
                if (field.click) {
                    field.ngclick = function (e) {
                        //
                    };
                }
                return $compile('<button ng-click="field.ngclick">{{field.name}}</button>')(scope);
            };

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

        }])
        //
        // Default Lux form
        .directive('luxForm', ['$log', 'formService', function (log, formService) {

            return {
                restrict: "AE",
                //
                link: function (scope, element, attrs) {
                    // Initialise the scope from the attributes
                    var form = extend({}, formDefaults, getOptions(attrs));
                    if (form.field) {
                        element.html('');
                        // Form has a type (the tag), create the form element
                        if (form.field.type) {
                            var el = angular.element('<' + form.field.type + '>').attr('role', 'form');
                            element.append(el);
                            element = el;
                        }
                        extend(scope, form);
                        scope.form = {};
                        scope.formParameters = {};
                        scope.formid = scope.id;
                        scope.count = 0;
                        if (!scope.formid)
                            scope.formid = 'f' + s4();
                        formService.compile(scope, element);
                    } else {
                        log.error('Form data does not contain field entry');
                    }
                }
            };
        }])
        //
        // Controller for a field in a Form with default layout
        .controller('FormField', ['$scope', 'formService', function (scope, formService) {
            var field = scope.field;
            if (field.type === 'checkbox' || field.type === 'radio') {
                field.radio = true;
                field.groupClass = field.type;
            }
            else
                field.groupClass = 'form-group';
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
        .directive('luxInput', function($parse) {
            return {
                restrict: "A",
                compile: function($element, $attrs) {
                    var initialValue = $attrs.value || $element.val();
                    if (initialValue) {
                        return {
                            pre: function($scope, $element, $attrs) {
                                $parse($attrs.ngModel).assign($scope, initialValue);
                                $scope.$apply();
                            }
                        };
                    }
                }
            };
        });

    angular.module('lux.scope.loader', [])
        //
        .value('context', lux.context)
        //
        .run(['$rootScope', '$log', 'context', function (scope, log, context) {
            log.info('Extend root scope with context');
            extend(scope, context);
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
            if (lux.context.uiRouter)
                modules.push('lux.ui.router');
            else
                modules.push('lux.router');
            // Add all modules from context
            forEach(lux.context.ngModules, function (mod) {
                modules.push(mod);
            });
            modules.splice(0, 0, 'lux.scope.loader');
            angular.module(name, modules);
            angular.bootstrap(document, [name]);
            //
            forEach(ready_callbacks, function (callback) {
                callback();
            });
            ready_callbacks = true;
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
    "        <a href=\"{{post.html_url}}\" class=\"pull-left hidden-xs dir-entry-image\">\n" +
    "          <img ng-src=\"{{post.image}}\" alt=\"{{post.title}}\">\n" +
    "        </a>\n" +
    "        <a href=\"{{post.html_url}}\" class=\"visible-xs\">\n" +
    "            <img ng-src=\"{{post.image}}\" alt=\"{{post.title}}\" class=\"dir-entry-image\">\n" +
    "        </a>\n" +
    "        <p class=\"visible-xs\"></p>\n" +
    "        <div class=\"media-body\">\n" +
    "            <h4 class=\"media-heading\"><a href=\"{{post.html_url}}\">{{post.title}}</a></h4>\n" +
    "            <p data-ng-if=\"post.description\">{{post.description}}</p>\n" +
    "            <p class=\"text-info small\">by {{post.authors}} on {{post.dateText}}</p>\n" +
    "        </div>\n" +
    "    </li>\n" +
    "</ul>");
}]);

    //  Blog Module
    //  ===============
    //
    //  Simple blog pagination directives and code highlight with highlight.js
    angular.module('lux.blog', ['templates-blog', 'lux.services', 'highlight', 'lux.scroll'])
        .controller('BlogEntry', ['$scope', 'dateFilter', '$lux', 'scroll', function ($scope, dateFilter, $lux, scroll) {
            var post = $scope.post;
            if (!post) {
                $lux.log.error('post not available in $scope, cannot use pagination controller!');
                return;
            }
            addPageInfo(post, $scope, dateFilter, $lux);
        }])
        .directive('blogPagination', function () {
            return {
                templateUrl: "blog/pagination.tpl.html",
                restrict: 'AE'
            };
        })
        .directive('blogHeader', function () {
            return {
                templateUrl: "blog/header.tpl.html",
                restrict: 'AE'
            };
        });

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
angular.module('templates-nav', ['nav/navbar.tpl.html', 'nav/navbar2.tpl.html']);

angular.module("nav/navbar.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("nav/navbar.tpl.html",
    "<nav ng-attr-id=\"{{navbar.id}}\" class=\"navbar navbar-{{navbar.themeTop}}\"\n" +
    "ng-class=\"{'navbar-fixed-top':navbar.fixed, 'navbar-static-top':navbar.top}\" role=\"navigation\"\n" +
    "ng-model=\"navbar.collapse\" bs-collapse>\n" +
    "    <div class=\"{{navbar.container}}\">\n" +
    "        <div class=\"navbar-header\">\n" +
    "            <button type=\"button\" class=\"navbar-toggle\" bs-collapse-toggle>\n" +
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
    "            <ul class=\"nav navbar-nav\">\n" +
    "                <li ng-repeat=\"link in navbar.items\" ng-class=\"{active:activeLink(link)}\">\n" +
    "                    <a href=\"{{link.href}}\" title=\"{{link.title || link.name}}\">\n" +
    "                    <i ng-if=\"link.icon\" class=\"{{link.icon}}\"></i> {{link.name}}</a>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "            <ul class=\"nav navbar-nav navbar-right\">\n" +
    "                <li ng-repeat=\"link in navbar.itemsRight\" ng-class=\"{active:activeLink(link)}\">\n" +
    "                    <a href=\"{{link.href}}\" title=\"{{link.title || link.name}}\">\n" +
    "                    <i ng-if=\"link.icon\" class=\"{{link.icon}}\"></i> {{link.name}}</a>\n" +
    "                </li>\n" +
    "            </ul>\n" +
    "        </div>\n" +
    "    </div>\n" +
    "</nav>");
}]);

angular.module("nav/navbar2.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("nav/navbar2.tpl.html",
    "<div class=\"navbar2-wrapper navbar-{{navbar.theme}}\">\n" +
    "    <nav class=\"navbar navbar-{{navbar.themeTop}} navbar-fixed-top navbar-static-top\" role=\"navigation\" ng-model=\"navbar.collapse\" bs-collapse>\n" +
    "        <div class=\"navbar-header\">\n" +
    "            <button type=\"button\" class=\"navbar-toggle\" bs-collapse-toggle>\n" +
    "                <span class=\"sr-only\">Toggle navigation</span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "                <span class=\"icon-bar\"></span>\n" +
    "            </button>\n" +
    "            <a href=\"/\" class=\"navbar-brand\" target=\"_self\">{{navbar.brand}}</a>\n" +
    "        </div>\n" +
    "        <ul class=\"nav navbar-top-links navbar-right\">\n" +
    "            <li ng-repeat=\"item in navbar.items\">\n" +
    "                <a href=\"{{item.href}}\" target=\"{{item.target}}\" title=\"{{item.title || item.value}}\">\n" +
    "                <i ng-if=\"item.icon\" class=\"{{item.icon}}\"></i>{{item.value}}</a>\n" +
    "            </li>\n" +
    "        </ul>\n" +
    "        <div class=\"navbar sidebar\" role=\"navigation\">\n" +
    "            <div class=\"sidebar-collapse\" bs-collapse-target>\n" +
    "                <ul id=\"side-menu\" class=\"nav nav-side\">\n" +
    "                    <li ng-if=\"navbar.search\" class=\"sidebar-search\">\n" +
    "                        <div class=\"input-group custom-search-form\">\n" +
    "                            <input class=\"form-control\" type=\"text\" placeholder=\"Search...\">\n" +
    "                            <span class=\"input-group-btn\">\n" +
    "                                <button class=\"btn btn-default\" type=\"button\" ng-click=\"search()\">\n" +
    "                                    <i class=\"fa fa-search\"></i>\n" +
    "                                </button>\n" +
    "                            </span>\n" +
    "                        </div>\n" +
    "                    </li>\n" +
    "                    <li ng-repeat=\"link in navbar.items2\">\n" +
    "                        <a ng-if=\"!link.links\" href=\"{{link.href}}\">{{link.name || link.href}}</a>\n" +
    "                        <a ng-if=\"link.links\" href=\"{{link.href}}\" class=\"with-children\">{{link.name}}</a>\n" +
    "                        <a ng-if=\"link.links\" href=\"#\" class=\"pull-right toggle\" ng-click=\"togglePage($event)\">\n" +
    "                            <i class=\"fa\" ng-class=\"{'fa-chevron-left': !link.active, 'fa-chevron-down': link.active}\"></i></a>\n" +
    "                        <ul ng-if=\"link.links\" class=\"nav nav-second-level collapse\" ng-class=\"{in: link.active}\">\n" +
    "                            <li ng-repeat=\"link in link.links\">\n" +
    "                                <a ng-if=\"!link.vars\" href=\"{{link.href}}\" ng-click=\"loadPage($event)\">{{link.name}}</a>\n" +
    "                            </li>\n" +
    "                        </ul>\n" +
    "                    </li>\n" +
    "                </ul>\n" +
    "            </div>\n" +
    "        </div>\n" +
    "    </nav>\n" +
    "    <div class=\"navbar2-page\" navbar2-page></div>\n" +
    "</div>");
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
        top: false,
        search: false,
        url: lux.context.url,
        target: '',
        fluid: true
    };

    angular.module('lux.nav', ['templates-nav', 'lux.services', 'mgcrea.ngStrap.collapse'])
        //
        .service('navService', ['$location', function ($location) {

            this.initScope = function (opts) {
                var navbar = extend({}, navBarDefaults, getOptions(opts));
                if (!navbar.url)
                    navbar.url = '/';
                if (!navbar.themeTop)
                    navbar.themeTop = navbar.theme;
                navbar.container = navbar.fluid ? 'container-fluid' : 'container';
                this.maybeCollapse(navbar);
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
        //  Directive for the simple navbar
        //  This directive does not require the Navigation controller
        .directive('navbar', ['navService', function (navService) {
            //
            return {
                templateUrl: "nav/navbar.tpl.html",
                restrict: 'AE',
                // Create an isolated scope
                scope: {},
                // Link function
                link: function (scope, element, attrs) {
                    scope.navbar = navService.initScope(attrs);
                    scope.activeLink = navService.activeLink;
                    //
                    windowResize(function () {
                        if (navService.maybeCollapse(scope.navbar))
                            scope.$apply();
                    });
                }
            };
        }])
        //
        //  Directive for the navbar with sidebar (nivebar2 template)
        .directive('navbar2', ['navService', '$compile', function (navService, $compile) {
            return {
                restrict: 'AE',
                // Link function
                link: function (scope, element, attrs) {
                    scope.navbar2Content = element.children();
                    scope.navbar = navService.initScope(attrs);
                    scope.activeLink = navService.activeLink;
                    var inner = $compile('<nav-side-bar></nav-side-bar>')(scope);
                    element.append(inner);
                    //
                    windowResize(function () {
                        if (navService.maybeCollapse(scope.navbar))
                            scope.$apply();
                    });
                }
            };
        }])
        //
        //  Directive for the navbar with sidebar (nivebar2 template)
        .directive('navSideBar', function () {
            return {
                templateUrl: "nav/navbar2.tpl.html",
                restrict: 'E'
            };
        })
        //
        // Directive for the main page in the sidebar2 template
        .directive('navbar2Page', function () {
            return {
                compile: function () {
                    return {
                        pre: function (scope, element, attrs) {
                            element.append(scope.navbar2Content);
                            attrs.$set('style', 'min-height: ' + windowHeight() + 'px');
                        }
                    };
                }
            };
        });

    // Controller for User
    angular.module('users', ['lux.services'])
        .controller('userController', ['$scope', '$lux', function ($scope, $lux) {
            // Model for a user when updating
            formController($scope, $lux, lux.context.user);

            // Unlink account for a OAuth provider
            $scope.unlink = function(e, name) {
                e.preventDefault();
                e.stopPropagation();
                var url = '/oauth/' + name + '/remove';
                $.post(url).success(function (data) {
                    if (data.success)
                        $route.reload();
                });
            };

            // Check if password is correct
            $scope.check_password_repeat = function () {
                var u = this.formModel,
                    field = this.form.password_repeat,
                    psw1 = u.password,
                    psw2 = u.password_repeat;
                if (psw1 !== psw2 && field.$dirty) {
                    this.formErrors.password_repeat = "passwords don't match";
                    field.$error.password_repeat = true;
                    this.formClasses.password_repeat = 'has-error';
                } else if (field.$dirty) {
                    this.formClasses.password_repeat = 'has-success';
                    delete this.form.$error.password_repeat;
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
    lux.createApi('googlesheets', {
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
    angular.module('lux.google', [])
        //
        .run(['$rootScope', '$log', '$location', function (scope, log, location) {
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
    //
    // Load d3 extensions into angular 'd3viz' module
    //  d3ext is the d3 extension object
    //  name is the optional module name for angular (default to d3viz)
    lux.addD3ext = function (d3, name) {

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
        //
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

        name = name || 'd3viz';
        var app = angular.module(name, ['lux.services']);

        // Loop through d3 extensions and create directives
        // for each Visualization class
        angular.forEach(d3.ext, function (VizClass, name) {

            if (d3.ext.isviz(VizClass)) {
                var dname = 'viz' + name.substring(0,1).toUpperCase() + name.substring(1);

                app.directive(dname, ['$lux', function ($lux) {
                    return {
                            //
                            // Create via element tag or attribute
                            restrict: 'AE',
                            //
                            link: function (scope, element, attrs) {
                                var options = getOptions(d3, attrs);
                                var viz = new VizClass(element[0], options);
                                viz.loadData = loadData($lux);
                                viz.build();
                            }
                        };
                }]);
            }
        });

        return lux;
    };


	return lux;
}));