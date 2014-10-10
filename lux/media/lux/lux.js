//      Lux Library - v0.1.0

//      Compiled 2014-10-10.
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
        $ = angular.element;
    //
    lux.$ = $;
    lux.forEach = angular.forEach;
    lux.context = root.luxContext || {};

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

    var generateResize = function () {
        var resizeFunctions = [],
            callResizeFunctions = function () {
                resizeFunctions.forEach(function (f) {
                    f();
                });
            };
        //
        callResizeFunctions.add = function (f) {
            resizeFunctions.push(f);
        };
        return callResizeFunctions;
    };

    //
    //  Utilities
    //
    var windowResize = lux.windowResize = function (callback, delay) {
        var handle;
        delay = delay ? +delay : 0;

        function execute () {
            handle = null;
            callback();
        }

        if (window.onresize === null) {
            window.onresize = generateResize();
        }
        if (window.onresize.add) {
            if (delay) {
                window.onresize.add(function (e) {
                    if (!handle)
                        handle = setTimeout(execute, delay);
                });
            } else {
                window.onresize.add(callback);
            }
        }
    };

    var windowHeight = lux.windowHeight = function () {
        return window.innerHeight > 0 ? window.innerHeight : screen.availHeight;
    };

    var isAbsolute = new RegExp('^([a-z]+://|//)');

    var isTag = function (element, tag) {
        element = $(element);
        return element.length === 1 && element[0].tagName.toLowerCase() === tag.toLowerCase();
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

    angular.module('lux.scroll', [])
        .service('scroll', ['$location', '$log', '$timeout', function ($location, $log, $timeout) {
            //
            //  ScrollToHash
            this.toHash = function (hash, offset) {
                var e;
                if (hash.currentTarget) {
                    e = hash;
                    hash = hash.currentTarget.hash;
                }
                // set the location.hash to the id of
                // the element you wish to scroll to.
                var target = document.getElementById(hash.substring(1));
                if (target) {
                    $location.hash(hash);
                    $log.info('Scrolling to target');
                    scrollTo(target);
                } else
                    $lux.log.warning('Cannot scroll, target not found');
            };

            function scrollTo (target) {
                var i,
                    startY = currentYPosition(),
                    stopY = elmYPosition(target),
                    distance = stopY > startY ? stopY - startY : startY - stopY;
                if (distance < 100) {
                    window.scrollTo(0, stopY);
                    return;
                }
                var speed = Math.round(distance),
                    step = Math.round(distance / 25),
                    y = startY;
                _nextScroll(startY, speed, step, stopY);
            }

            function _nextScroll (y, speed, stepY, stopY) {
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
                var delay = 1000*d/speed;
                $timeout(function () {
                    window.scrollTo(0, y2);
                    if (more)
                        _nextScroll(y2, speed, stepY, stopY);
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
    var FORMKEY = 'm__form';
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

        $scope.checkField = function (name) {
            var checker = $scope['check_' + name];
            // There may be a custom field checker
            if (checker)
                checker.call($scope);
            else {
                var field = $scope.form[name];
                if (field.$valid)
                    $scope.formClasses[name] = 'has-success';
                else if (field.$dirty) {
                    $scope.formErrors[name] = name + ' is not valid';
                    $scope.formClasses[name] = 'has-error';
                }
            }
        };

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

        // add the watch change directive
    angular.module('lux.form', ['lux.services'])
        .controller('FormCtrl', ['$scope', '$lux', 'data', function ($scope, $lux, data) {
            // Default form controller
            formController($scope, $lux, data);
        }])
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
        return page;
    }

    //  Lux angular
    //  ==============
    //  Lux main module for angular. Design to work with the ``lux.extension.angular``
    angular.module('lux', ['lux.services', 'lux.form'])
        .controller('Page', ['$scope', '$lux', 'dateFilter', '$anchorScroll',
            function ($scope, $lux, dateFilter, $anchorScroll) {
            //
            $lux.log.info('Setting up angular page');
            //
            // Inject lux context into the scope of the page
            angular.extend($scope, lux.context);
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

            $scope.scrollToHash = $lux.scrollToHash;

        }]);

    //
    //  UI-Routing
    //
    //  Configure ui-Router using lux routing objects
    //  Only when context.html5mode is true
    //  Python implementation in the lux.extensions.angular Extension
    function configRouter(mod) {
        mod.config(['$locationProvider', '$stateProvider', '$urlRouterProvider',
            function ($locationProvider, $stateProvider, $urlRouterProvider) {

            var hrefs = lux.context.hrefs,
                pages = lux.context.pages,
                state_config = function (page) {
                    return {
                        //
                        // template url for the page
                        //templateUrl: page.templateUrl,
                        //
                        template: page.template,
                        //
                        url: page.url,
                        //
                        resolve: {
                            // Fetch page information
                            page: function ($lux, $stateParams) {
                                if (page.api) {
                                    var api = $lux.api(page.api);
                                    if (api)
                                        return api.get($stateParams);
                                }
                            },
                            // Fetch items if needed
                            items: function ($lux, $stateParams) {
                                if (page.apiItems) {
                                    var api = $lux.api(page.apiItems);
                                    if (api)
                                        return api.getList();
                                }
                            },
                        },
                        //
                        controller: page.controller
                    };
                };

            $locationProvider.html5Mode(lux.context.html5mode);

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
        .directive('dynamicPage', ['$compile', '$log', function ($compile, $log) {
            return {
                link: function (scope, element, attrs) {
                    scope.$on('$stateChangeSuccess', function () {
                        var page = scope.page;
                        if (page.html_main) {
                            element.html(page.html_main);
                            $compile(element.contents())(scope);
                        }
                    });
                }
            };
        }]);

    }

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
            modules.push('lux');
            // Add all modules from context
            forEach(lux.context.ngModules, function (mod) {
                modules.push(mod);
            });
            var mod = angular.module(name, modules);
            if (lux.context.html5mode && configRouter)
                configRouter(mod);
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

angular.module('templates-blog', ['lux/blog/header.tpl.html', 'lux/blog/pagination.tpl.html']);

angular.module("lux/blog/header.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("lux/blog/header.tpl.html",
    "<h2 data-ng-bind=\"page.title\"></h2>\n" +
    "<p class=\"small\">by {{page.authors}} on {{page.dateText}}</p>\n" +
    "<p class=\"lead storyline\">{{page.description}}</p>");
}]);

angular.module("lux/blog/pagination.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("lux/blog/pagination.tpl.html",
    "<ul class=\"media-list\">\n" +
    "    <li ng-repeat=\"post in items\" class=\"media\" data-ng-controller='BlogEntry'>\n" +
    "        <a href=\"{{post.html_url}}\" class=\"pull-left hidden-xs dir-entry-image\">\n" +
    "          <img data-ng-if=\"post.image\" src=\"{{post.image}}\" alt=\"{{post.title}}\">\n" +
    "          <img data-ng-if=\"!post.image\" src=\"holder.js/120x90\">\n" +
    "        </a>\n" +
    "        <a href=\"{{post.html_url}}\" class=\"visible-xs\">\n" +
    "            <img data-ng-if=\"post.image\" src=\"{{post.image}}\" alt=\"{{post.title}}\" class=\"dir-entry-image\">\n" +
    "            <img data-ng-if=\"!post.image\" src=\"holder.js/120x90\">\n" +
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
                templateUrl: "lux/blog/pagination.tpl.html",
                restrict: 'AE'
            };
        })
        .directive('blogHeader', function () {
            return {
                templateUrl: "lux/blog/header.tpl.html",
                restrict: 'AE'
            };
        })
        .directive('toc', ['$lux', function ($lux) {
            return {
                link: function (scope, element, attrs) {
                    //
                    forEach(element[0].querySelectorAll('.toc a'), function (el) {
                        el = $(el);
                        var href = el.attr('href');
                        if (href.substring(0, 1) === '#' && href.substring(0, 2) !== '##')
                            el.on('click', scroll.toHash);
                    });
                }
            };
        }]);

    //
    //  Code highlighting with highlight.js
    //
    //  This module is added to the blog module so that the highlight
    //  directive can be used
    angular.module('highlight', [])
        .directive('highlight', function () {
            return {
                link: function link(scope, element, attrs) {
                    highlight(element);
                }
            };
        });

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
        });
    };
angular.module('templates-nav', ['lux/nav/navbar2.tpl.html']);

angular.module("lux/nav/navbar2.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("lux/nav/navbar2.tpl.html",
    "<nav class=\"navbar navbar-{{navbar.themeTop}} navbar-fixed-top\" role=\"navigation\" ng-model=\"navbar.collapse\" bs-collapse>\n" +
    "    <div class=\"navbar-header\">\n" +
    "        <button type=\"button\" class=\"navbar-toggle\" bs-collapse-toggle>\n" +
    "            <span class=\"sr-only\">Toggle navigation</span>\n" +
    "            <span class=\"icon-bar\"></span>\n" +
    "            <span class=\"icon-bar\"></span>\n" +
    "            <span class=\"icon-bar\"></span>\n" +
    "        </button>\n" +
    "        <a href=\"/\" class=\"navbar-brand\" target=\"_self\">{{navbar.brand}}</a>\n" +
    "    </div>\n" +
    "    <ul class=\"nav navbar-top-links navbar-right\">\n" +
    "        <li ng-repeat=\"item in navbar.items\">\n" +
    "            <a href=\"{{item.href}}\" target=\"{{item.target}}\" title=\"{{item.title || item.value}}\">\n" +
    "            <i ng-if=\"item.icon\" class=\"{{item.icon}}\"></i>{{item.value}}</a>\n" +
    "        </li>\n" +
    "    </ul>\n" +
    "    <div class=\"navbar sidebar\" role=\"navigation\">\n" +
    "        <div class=\"sidebar-collapse\" bs-collapse-target>\n" +
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
    "                    <a ng-if=\"!link.links\" href=\"{{link.href}}\">{{link.name || link.href}}</a>\n" +
    "                    <a ng-if=\"link.links\" href=\"{{link.href}}\" class=\"with-children\">{{link.name}}</a>\n" +
    "                    <a ng-if=\"link.links\" href=\"#\" class=\"pull-right toggle\" ng-click=\"togglePage($event)\">\n" +
    "                        <i class=\"fa\" ng-class=\"{'fa-chevron-left': !link.active, 'fa-chevron-down': link.active}\"></i></a>\n" +
    "                    <ul ng-if=\"link.links\" class=\"nav nav-second-level collapse\" ng-class=\"{in: link.active}\">\n" +
    "                        <li ng-repeat=\"link in link.links\">\n" +
    "                            <a ng-if=\"!link.vars\" href=\"{{link.href}}\" ng-click=\"loadPage($event)\">{{link.name}}</a>\n" +
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
        search: false
    };

    angular.module('lux.nav', ['templates-nav', 'lux.services', 'mgcrea.ngStrap.collapse'])
        .controller('Navigation', ['$scope', '$lux', function ($scope, $lux) {
            $lux.log.info('Setting up navigation on page');
            //
            var navbar = $scope.navbar = angular.extend({}, navBarDefaults, $scope.navbar),
                maybeCollapse = function () {
                    var width = window.innerWidth > 0 ? window.innerWidth : screen.width,
                        c = navbar.collapse;
                    if (width < navbar.collapseWidth)
                        navbar.collapse = 'collapse';
                    else
                        navbar.collapse = '';
                    return c !== navbar.collapse;
                };
            if (!navbar.themeTop)
                navbar.themeTop = navbar.theme;

            maybeCollapse();
            //
            windowResize(function () {
                if (maybeCollapse())
                    $scope.$apply();
            });
            //
            // Search
            $scope.search = function () {
                if (scope.search_text) {
                    window.location.href = '/search?' + $.param({q: $scope.search_text});
                }
            };

        }])
    //
    //  Directive for the navbar with sidebar (nivebar2 template)
    .directive('navbar2', function () {
        return {
            templateUrl: "lux/nav/navbar2.tpl.html",
            restrict: 'AE'
        };
    })
    //
    // Directive for the main page in the sidebar2 template
    .directive('navbar2Page', function () {
        return {
            compile: function () {
                return {
                    pre: function (scope, element, attrs) {
                        element.addClass('navbar2-page');
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


    angular.module('google.maps', [])
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