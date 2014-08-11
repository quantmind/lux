define(['jquery', 'angular', 'angular-sanitize'], function ($) {
    "use strict";

    var lux = {},
        defaults = {
            ngModules: [],
            ngDirectives: [],
            ngControllers: []
        },
        root = window,
        routes = [],
        ready_callbacks = [],
        angular_bootstrapped = false,
        context = $.extend(defaults, root.context);

    // when in html5 mode add ngRoute to the list of required modules
    if (context.html5mode)
        context.ngModules.push('ngRoute');

    angular.element = $;
    lux.$ = $;
    lux.context = context;
    lux.services = angular.module('lux.services', []);
    lux.controllers = angular.module('lux.controllers', ['lux.services']);
    lux.app = angular.module('lux', []);

    // Add a new HTML5 route to the page router
    lux.addRoute = function (url, data) {
        routes.push([url, data]);
    };

    // Callbacks run after angular has finished bootstrapping
    lux.add_ready_callback = function (callback) {
        if (ready_callbacks === true) callback();
        else ready_callbacks.push(callback);
    };

    $.each(['ngSanitize', 'lux.controllers', 'lux.services'], function (i, name) {
        context.ngModules.push(name);
    });


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


    var ApiTypes = lux.ApiTypes = {};
    //
    // If CSRF token is not available
    // try to obtain it from the meta tags
    if (!context.csrf) {
        var name = $("meta[name=csrf-param]").attr('content'),
            token = $("meta[name=csrf-token]").attr('content');
        if (name && token) {
            context.csrf = {};
            context.csrf[name] = token;
        }
    }
    //  Lux Api service factory for angular
    //  ---------------------------------------
    //
    lux.services.service('$lux', function ($location, $q, $http, $log, $anchorScroll) {
        var $lux = this;

        this.location = $location;
        this.log = $log;
        this.http = $http;
        this.q = $q;
        this.anchorScroll = $anchorScroll;

        // A post method with CSRF parameter
        this.post = function (url, data, cfg) {
            if (context.csrf) {
                data || (data = {});
                angular.extend(data, context.csrf);
            }
            return $http.post(url, data, cfg);
        };

        //  Create an api client
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
            var Api = ApiTypes[context.name || 'lux'];
            if (!Api)
                $lux.log.error('Api provider "' + context.name + '" is not available');
            else
                return new Api(context.name, context.url, $lux);
        };

    });

    //
    //  Lux API Interface
    //
    var ApiClient = lux.ApiClient = Class.extend({
        //
        //  Object containing the urls for the api.
        //  If not given, the object will be loaded via the ``context.apiUrl``
        //  variable.
        apiUrls: context.apiUrls,
        //
        init: function (name, url, $lux) {
            this.name = name;
            this.$lux = $lux;
            this.auth = null;
            this._url = url;
        },
        //
        // Can be used to manipulate the url
        url: function (id) {
            if (id !== undefined)
                return self._url + '/' + id;
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
        // Build the object used by $http when making the request
        // Returns the object
        httpOptions: function (request) {
            var options = request.options;
            options.url = this.url(request.urlparams);
            return options;
        },
        //
        //
        // Perform the actual request and return a promise
        request: function (method, urlparams, opts, data) {
            var d = this.$lux.q.defer(),
                //
                promise = d.promise,
                //
                request = {
                    deferred: d,
                    //
                    options: $.extend({'method': method, 'data': data}, opts),
                    //
                    'urlparams': urlparams,
                    //
                    api: this,
                    //
                    error: function (data, status, headers) {
                        if ($.isString(data)) {
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
            promise.success = function(fn) {
                promise.then(function(response) {
                    fn(response.data, response.status, response.headers);
                });
                return promise;
            };

            promise.error = function(fn) {
                promise.then(null, function(response) {
                    fn(response.data, response.status, response.headers);
                });
                return promise;
            };

            this.call(request);
            //
            return promise;
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
        getMany: function (options) {
            return this.request('GET', null, options);
        },
        //
        // Internal method for executing an API call
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
                } else if (context.apiUrl) {
                    // Fetch the api urls
                    var self = this;
                    $lux.log.info('Fetching api info');
                    return $lux.http.get(context.apiUrl).success(function (resp) {
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
            if (options.url)
                $lux.http(options).success(request.success).error(request.error);
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
            if (context.user) {
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
    //  Lux Static JSON API
    //  ----------------------
    lux.createApi('static', {
        //
        httpOptions: function (request) {
            var options = request.options,
                url = request.api.url,
                path = request.urlparams.path;
            if (path)
                url += '/' + path;
            if (url.substring(url.length-5) !== '.json')
                url += '.json';
            options.url = url;
            return options;
        }
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
        url: function () {
            // when given the url is of the form key/worksheet where
            // key is the key of the spreadsheet you want to retrieve,
            // worksheet is the positional or unique identifier of the worksheet
            if (this._url)
                return this.endpoint + '/feeds/list/' + this._url + '/public/values?alt=json';
        },
        //
        getMany: function (options) {
            var Model = this.Model,
                $lux = this.$lux;
            return this.request('GET', null, options).success(function (data) {
                return new Model($lux, data);
            });
        },
        //
        Model: function ($lux, data) {
            var i, j, ilen, jlen;
            this.column_names = [];
            this.name = data.feed.title.$t;
            this.elements = [];
            this.raw = data; // A copy of the sheet's raw data, for accessing minutiae

            if (typeof(data.feed.entry) === 'undefined') {
                $lux.log.warn("Missing data for " + this.name + ", make sure you didn't forget column headers");
                return;
            }

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
        }
    });


    var isAbsolute = new RegExp('^([a-z]+://|//)');

    // Page Controller
    //
    // Handle html5 sitemap
    lux.controllers.controller('page', ['$scope', '$lux', function ($scope, $lux) {
        //
        $lux.log.info('Setting up angular page');
        //
        angular.extend($scope, context);
        var page = $scope.page;
        if (page && $scope.pages) {
            $scope.page = page = $scope.pages[page];
        } else {
            $scope.page = page = {};
        }
        //
        $scope.windowHeight = function () {
            return root.window.innerHeight > 0 ? root.window.innerHeight : root.screen.availHeight;
        };

        $scope.search_text = '';
        $scope.sidebarCollapse = '';
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
        //
        // Search
        $scope.search = function () {
            if ($scope.search_text) {
                window.location.href = '/search?' + $.param({q: $scope.search_text});
            }
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

        $scope.collapse = function () {
            var width = root.window.innerWidth > 0 ? root.window.innerWidth : root.screen.width;
            if (width < context.navbarCollapseWidth)
                $scope.sidebarCollapse = 'collapse';
            else
                $scope.sidebarCollapse = '';
        };

        $scope.collapse();
        $(root).bind("resize", function () {
            $scope.collapse();
            $scope.$apply();
        });

        $scope.activeLink = function (url) {
            var loc;
            if (isAbsolute.test(url))
                loc = $lux.location.absUrl();
            else
                loc = $lux.location.path();
            var rest = loc.substring(url.length),
                base = loc.substring(0, url.length),
                folder = url.substring(url.length-1) === '/';
            return base === url && (folder || (rest === '' || rest.substring(0, 1) === '/'));
        };

        $scope.scrollToHash = function (e, offset) {
            // set the location.hash to the id of
            // the element you wish to scroll to.
            var target = $(e.currentTarget.hash);
            if (target.length) {
                offset = offset ? offset : 0;
                e.preventDefault();
                e.stopPropagation();
                $lux.log.info('Scrolling to target');
                $('html,body').animate({
                    scrollTop: target.offset().top + offset
                }, 1000);
                //$lux.location.hash(hash);
                // call $anchorScroll()
                //$lux.anchorScroll();
            } else
                $lux.log.warning('Cannot scroll, target not found');
        };

    }]);

    lux.controllers.controller('html5Page', ['$scope', '$lux', 'response',
        function ($scope, $lux, response) {
            var page = response.data;
            if (response.status !== 200) {
                return;
            }
            $scope.page = page;
            if (page.html_title) {
                document.title = page.html_title;
            }
    }]);
    //  SITEMAP
    //  -----------------
    //
    //  Build an HTML5 sitemap when the ``context.sitemap`` variable is set.
    function _load_sitemap (hrefs, pages) {
        //
        angular.forEach(hrefs, function (href) {
            var page = pages[href];
            if (page && page.href && page.target !== '_self') {
                lux.addRoute(page.href, route_config(page));
            }
        });
    }

    // Configure a route for a given page
    function route_config (page) {

        return {
            //
            // template url for the page
            templateUrl: page.template_url,
            //
            template: '<div ng-bind-html="page.content"></div>',
            //
            controller: page.controller || 'html5Page',
            //
            resolve: {
                response: function ($lux, $route) {
                    if (page.api) {
                        var api = $lux.api(page.api);
                        return api.get($route.current.params);
                    }
                }
            }
        };
    }
    //
    // Load sitemap if available
    _load_sitemap(context.hrefs, context.pages);

    var FORMKEY = 'm__form';
    //
    // add the watch change directive
    lux.app.directive('watchChange', function() {
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

    // Change the form data depending on content type
    function formData(ct) {

        return function (data, getHeaders ) {
            angular.extend(data, context.csrf);
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
    function formController ($scope, $lux, model) {
        model || (model = {});

        var page = $scope.$parent ? $scope.$parent.page : {};

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
    }

    lux.controllers.controller('formController', ['$scope', '$lux', 'data',
            function ($scope, $lux, data) {
        // Model for a user when updating
        formController($scope, $lux, data);
    }]);


    lux.controllers.controller('listgroup', ['$scope', '$lux', 'data', function ($scope, $lux, data) {
        $scope.data = data.data;
    }]);


    // Controller for User
    lux.controllers.controller('userController', ['$scope', '$lux', function ($scope, $lux) {
        // Model for a user when updating
        formController($scope, $lux, context.user);

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

    lux.app.directive('luxElement', ['$lux', function ($lux) {
        //
        return {
            //
            // Create via element tag or attribute
            // <d3-force data-width=300 data-height=200></d3-force>
            restrict: 'AE',
            //
            link: function (scope, element, attrs) {
                var callbackName = attrs.callback;
                // The callback should be available from in the global scope
                if (callbackName) {
                    var callback = root[callbackName];
                    if (callback) {
                        callback($lux, scope, element, attrs);
                    } else
                        $lux.log.warn('Could not find callback ' + callbackName);
                } else
                    $lux.log.warn('Could not find callback');
            }
        };
    }]);

    //
    //  Lux Vizualization Class
    //  -------------------------------
    lux.Viz = Class.extend({
        //
        // Initialise the vizualization with a DOM element, an object of attributes
        // and the (optional) $lux service
        init: function (element, attrs, $lux) {
            element = $(element);
            this.element = element;
            this.attrs = attrs;
            this.$lux = $lux;
            this.elwidth = null;
            this.elheight = null;

            var parent = this.element.parent();

            if (!attrs.width) {
                attrs.width = element.width();
                if (attrs.width)
                    this.elwidth = element;
                else {
                    attrs.width = parent.width();
                    if (attrs.width)
                        this.elwidth = parent;
                    else
                        attrs.width = 400;
                }
            } else {
                attrs.width = +attrs.width;
            }
            //
            if (!attrs.height) {
                attrs.height = element.height();
                if (attrs.height)
                    this.elheight = element;
                else {
                    attrs.height = parent.height();
                    if (attrs.height)
                        this.elheight = parent;
                    else
                        attrs.height = 400;
                }
            } else if (attrs.height.indexOf('%') === attrs.height.length-1) {
                attrs.height_percentage = 0.01*parseFloat(attrs.height);
                attrs.height = attrs.height_percentage*attrs.width;
            }
            //
            if (attrs.resize) {
                var self = this;
                $(window).resize(function () {
                    self.resize();
                });
            }
            //
            this.build();
        },
        //
        // Resize the vizualization
        resize: function (size) {
            var w, h;
            if (size) {
                w = size[0];
                h = size[1];
            } else {
                w = this.elwidth ? this.elwidth.width() : this.attrs.width;
                if (this.attrs.height_percentage)
                    h = w*this.attrs.height_percentage;
                else
                    h = this.elheight ? this.elheight.height() : this.attrs.height;
            }
            if (this.attrs.width !== w || this.attrs.height !== h) {
                this.attrs.width = w;
                this.attrs.height = h;
                this.build();
            }
        },
        //
        // Return a new d3 svg element insite the element without any children
        svg: function (d3) {
            this.element.empty();
            return d3.select(this.element[0]).append("svg")
                .attr("width", this.attrs.width)
                .attr("height", this.attrs.height);
        },

        size: function () {
            return [this.attrs.width, this.attrs.height];
        },
        //
        // Normalized Height
        //
        // Try to always work with non dimensional coordinates,
        // Normalised vi the width
        sy: function () {
            var size = this.size();
            return size[1]/size[0];
        },
        //
        build: function () {
            var self = this;
            require(['d3'], function (d3) {
                self.d3build(d3);
            });
        },
        //
        // This is the actual method to implement
        d3build: function (d3) {

        }
    });

    lux.vizDirectiveFactory = function (Viz) {
        return ['$lux', function ($lux) {
            return {
                //
                // Create via element tag
                // <d3-force data-width=300 data-height=200></d3-force>
                restrict: 'AE',
                //
                link: function (scope, element, attrs) {
                    new Viz(element, attrs, $lux);
                }
            };
        }];
    };

    //
    lux.bootstrap = function () {
        //
        function setup_angular() {
            //
            $.each(context.ngModules, function (i, module) {
                if (lux.app.requires.indexOf(module) === -1)
                    lux.app.requires.push(module);
            });
            //
            angular.bootstrap(document, ['lux']);
            //
            angular.forEach(ready_callbacks, function (callback) {
                callback();
            });
            ready_callbacks = true;
        }
        //
        //
        $(document).ready(function() {
            //
            if (context.html5mode) {
                //
                // Load angular-route and configure the HTML5 navigation
                require(['angular-route'], function () {
                    //
                    if (routes.length) {
                        var all = routes;
                        routes = [];
                        //
                        lux.app.config(['$routeProvider', '$locationProvider',
                                function($routeProvider, $locationProvider) {
                            //
                            angular.forEach(all, function (route) {
                                var url = route[0];
                                var data = route[1];
                                if ($.isFunction(data)) data = data();
                                $routeProvider.when(url, data);
                            });
                            // use the HTML5 History API
                            $locationProvider.html5Mode(true);
                        }]);
                    }
                    setup_angular();
                });
            } else {
                setup_angular();
            }
        });
    };

	return lux;
});