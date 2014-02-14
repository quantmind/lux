    //
    // Web Interface entry points
    var web_extensions_to_load = [],
        scripts_to_execute = [],
        web = lux.web = {
            options: {
                debug: false,
                skins: [],
                media_url: '/media/',
                icon: 'fontawesome'
            },
            extension_list: [],
            extensions: {},
            libraries: [],
            extension: function (name, ext) {
                if (lux.$) {
                    ext = this.create_extension(name, ext);
                    this.extension_list.push(ext);
                    this.extensions[name] = ext;
                    return ext;
                } else {
                    web_extensions_to_load.push({'name': name, 'ext': ext});
                }
            },
            // Execute a callback when lux.web is ready.
            ready: function (requires, callback) {
                if (lux.$) {
                    if (callback === undefined) {
                        requires();
                    } else {
                        require(requires, callback);
                    }
                }
            },
            //
            // Apply all extensions to elem
            refresh: function (elem) {
                _(this.extension_list).forEach(function (ext) {
                    ext.refresh(elem);
                });
                return elem;
            },
            //
            add_lib: function (info) {
                if (!_.contains(this.libraries, info.name)) {
                    this.libraries.push(info);
                }
            }
        };
    //
    // Initialise lux web components once jQuery is loaded
    lux.init_web = function () {
        lux.$ = $;
        $(document).ready(function () {
            var doc = $(this),
                data = doc.find('html').data() || {};
            web.options = _.extend(web.options, data);
            if (web.options.debug) {
                logger.config({level: 'debug'});
                if (!logger.handlers.length) {
                    logger.addHandler();
                }
            }
            web.element = doc;
            var to_load = web_extensions_to_load;
            web_extensions_to_load = [];
            _(to_load).forEach(function(o) {
                web.extension(o.name, o.ext);
            });
            web.refresh(doc);
        });
    };

    // Generalised value setter for jQuery elements
    lux.set_value_hooks = [];
    lux.set_value = function (element, value) {
        var hook;
        for (var i=0; i<lux.set_value_hooks.length; i++) {
            if (lux.set_value_hooks[i](element, value)) {
                return;
            }
        }
        element.val(value);
    };

    //  Web Extensions
    //  ------------------------

    //  Base class for web extensions. Web extensions sre used to create
    //  widgets and other Html components for user interaction.

    web.ExtInstance = lux.Class.extend({
        //
        // The selector for the extension. If a selector is provided, the
        // extension automatically creates extension instances on Html elements
        // matching the selector.
        selector: null,
        //
        // If a default Element is given , this extension installed a function
        // in the lux.web object which can be used to create instances of this
        // extension.
        defaultElement: null,
        //
        options: {
            fade: {duration: 200}
        },
        //
        // Constructor of a web extension instance
        init: function (id, html, options) {
            this._id = id;
            this._element = html;
            this.options = _.merge({}, this.options, options);
        },
        // String representation of this extension
        toString: function () {
            return this._id;
        },
        //
        element: function () {
            return this._element;
        },
        //
        container: function () {
            return this._element;
        },
        //
        id: function () {
            return this._id;
        },
        //
        lux_id: function () {
            return this._id;
        },
        //
        extension: function () {
            return this.constructor;
        },
        //
        // Destroy the instance
        destroy: function () {
            return this.constructor.destroy(this);
        },
        //
        decorate: function () {},
        //
        // fadeIn the jQuery element conteining the extension.
        // Once the fadeIn action is finished a trigger the ``show``
        // event and invoke the optional ``callback``.
        fadeIn: function (callback) {
            var self = this;
            self._element.fadeIn({
                duration: this.options.fade.duration,
                complete: function () {
                    if (callback) {
                        callback(self);
                    }
                    self._element.trigger('show', self);
                }
            });
        },
        //
        // fadeOut the jQuery element conteining the extension.
        // Once the fadeOut action is finished a trigger the ``hide``
        // event and invoke the optional ``callback``.
        fadeOut: function (callback) {
            var self = this;
            self._element.fadeOut({
                duration: this.options.fade.duration,
                complete: function () {
                    if (callback) {
                        callback(self);
                    }
                    self._element.trigger('hide', self);
                }
            });
        },
        //
        // extract skin information from element
        get_skin: function (elem) {
            return web.get_skin(elem ? elem : this.element());
        }
    });
    //
    //  Create a new Web extension
    //  -------------------------------
    //

    //  A web extension is a way to apply javascript to the DOM via
    //  selectors.
    //
    //  * ``name`` extension name, if the extension has a valid ``defaultElement``
    //    attribute, it can be accessed on ``lux.web`` at the ``name`` attribute.
    //  * ``ext`` object which overrides the ``superClass``.
    //  * ``superClass`` the base class to override. If not provided the
    //    ``lux.web.ExtInstance`` is used.
    web.create_extension = function (name, ext, superClass) {
        var instances = [],
            // prefix for the data key storing an extension instance
            prefix = name + '-',
            lux_idkey = 'lux-' + name + '-id',
            creation_count = 0,
            makeid = function () {
                creation_count += 1;
                return prefix + creation_count;
            };
        superClass = superClass ? superClass : web.ExtInstance;
        ext.options = _.merge({}, superClass.prototype.options, ext.options);
        ext.name = name;
        // Extension class
        var Extension = superClass.extend(ext);
        //
        // Class methods
        //
        // Retrieve an instance of a model created by this extension
        Extension.instance = function (elem) {
            if (elem) {
                elem = elem.lux_id ? elem.lux_id() : elem;
                var i = instances[elem],
                    o;
                // get by instance id
                if (!i) {
                    o = $(elem);
                    if (!o.length && typeof elem === "string") {
                        o = $("#" + elem);
                    }
                    if (!o.length) {
                        i = null;
                    } else {
                        i = instances[o.closest("." + name).data(lux_idkey)] || null;
                    }
                }
                return i;
            } else {
                return null;
            }
        };
        //
        // Create an Instance for this Extension.
        // An instance is a lux.Class
        Extension.create = function (html, options) {
            var o = this.instance(html);
            if (o !== null) {
                return o;
            }
            html = $(html);
            if (html.length === 0) {
                html = $(document.createElement(ext.defaultElement));
            } else {
                var opts = html.data(name) || html.data();
                if (options) {
                    options = _.extend(options, opts);
                } else {
                    options = opts;
                }
            }
            var _id = makeid();
            //
            o = new Extension(makeid(), html, options);
            instances[o.id()] = o;
            o.decorate();
            return o;
        };
        //
        Extension.destroy = function (instance) {
            instance = this.instance(instance);
            if (instance) {
                delete instances[instance.id()];
                var elem = instance.container();
                if (elem) {
                    elem.trigger('remove', instance);
                    elem.detach().trigger('removed', instance);
                    elem.remove();
                }
            }
        },
        //
        Extension.toString = function (instance) {
            return name;
        };
        //
        // Refresh an extension by running the decorate methods on all matched elements
        Extension.refresh = function (html) {
            var instances = [];
            if (Extension.prototype.selector) {
                var elements = $(Extension.prototype.selector, html);
                if (elements.length) {
                    logger.info('Apply extension ' + name + ' to ' +
                                elements.length + ' elements');
                    elements.each(function () {
                        instances.push(Extension.create(this));
                    });
                }
            }
            return instances;
        };
        //
        if (Extension.prototype.defaultElement) {
            web[Extension.prototype.name] = function(options_or_element, options) {
                var elem = options_or_element;
                if(!options_or_element || $.isPlainObject(options_or_element)) {
                    elem = null;
                    options = options_or_element;
                }
                return Extension.create(elem, options);
            };
        }
        //
        return Extension;
    };

    // Add default libraries
    web.add_lib({name: 'RequireJs', web: 'http://requirejs.org/', version: require.version});
    web.add_lib({name: 'Lo-Dash', web: 'http://lodash.com/', version: _.VERSION});
    web.add_lib({name: 'jQuery', web: 'http://jquery.com/', version: $.fn.jquery});