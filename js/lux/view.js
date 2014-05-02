    //  View
    //  ----------
    //
    //  A ``View`` is a way of to organize your interface into logical views,
    //  backed by models, each of which can be updated independently when
    //  the model changes, without having to redraw the page.
    //  Instead of digging into a JSON object, looking up an element in
    //  the DOM, and updating the HTML by hand, you can bind your view's
    //  render function to the model's "change" event — and now everywhere
    //  that model data is displayed in the UI, it is always
    //  immediately up to date
    var
    //
    // List of views which out-load when the DOM is ready
    autoViews = lux.autoViews = [],
    //
    SKIN_NAMES = lux.SKIN_NAMES = ['default', 'primary', 'success', 'inverse', 'error'],
    //
    // Extract a skin information from ``elem``
    getSkin = lux.getSkin = function (elem, prefix) {
        if (elem) {
            prefix = prefix ? prefix + '-' : '';
            for (var i=0; i < SKIN_NAMES.length; i++) {
                var name = SKIN_NAMES[i];
                if (elem.hasClass(prefix+name)) {
                    return name;
                }
            }
        }
    },
    //
    // Set the skin on an element
    setSkin = lux.setSkin = function(elem, skin, prefix) {
        if (SKIN_NAMES.indexOf(skin) > -1) {
            prefix = prefix ? prefix + '-' : '';
            //
            _(SKIN_NAMES).forEach(function (name) {
                elem.removeClass(prefix+name);
            });
            elem.addClass(prefix+skin);
        }
    },
    //
    // Cached regex to split keys for `delegate`.
    delegateEventSplitter = /^(\S+)\s*(.*)$/,
    //
    viewOptions = ['model', 'collection', 'elem', 'id', 'attributes',
                   'className', 'tagName', 'name', 'events'],
    //
    // A view class
    View = lux.View = Class.extend({
        //
        // Default HTML tag for the view
        tagName: 'div',
        //
        defaults: null,
        //
        // This method should not be overwritten, use the ``initialise``
        // method instead.
        init: function (options) {
            this.cid = _.uniqueId('view');
            options || (options = {});
            if (this.defaults) {
                options = _.extend({}, this.defaults, options);
            }
            _.extend(this, _.pick(options, viewOptions));
            if (!this.elem) {
                this.setElement($(document.createElement(this.tagName)), false);
            } else {
                this.elem = $(_.result(this, 'elem'));
                this.setElement(this.elem, false);
            }
            if (this.instance_key) this.elem.data(this.instance_key, this);
            this.initialise(options);
        },

        // Callat the end of the ``init`` method.
        // A chance to perform view specific initialisation
        initialise: function (options) {},

        remove: function() {
            this.elem.remove();
            return this;
        },

        delegateEvents: function(events) {
            events = events || this.events;
            if (!events) return this;
            this.undelegateEvents();
            for (var key in events) {
                var method = events[key];
                if (!_.isFunction(method)) method = this[method];
                if (!method) continue;
                //
                var match = key.match(delegateEventSplitter);
                var eventName = match[1], selector = match[2];
                method = _.bind(method, this);
                eventName += '.delegateEvents' + this.cid;
                if (selector === '') {
                    this.elem.on(eventName, method);
                } else {
                    this.elem.on(eventName, selector, method);
                }
            }
            return this;
        },

        undelegateEvents: function() {
            this.elem.off('.delegateEvents' + this.cid);
            return this;
        },

        render: function () {
            return this;
        },
        //
        setElement: function (elem, delegate) {
            if (this.elem) this.undelegateEvents();
            this.elem = $(elem);
            if (delegate !== false) this.delegateEvents();
            return this;
        },
        //
        // Immediately show the ``elem`` and fire 'show' event
        show: function () {
            this.elem.show();
            this.elem.trigger('show', this);
        },
        //
        // Immediately hide the ``elem`` and fire 'hide' event
        hide: function () {
            this.elem.hide();
            this.elem.trigger('hide', this);
        },
        //
        // fadeIn the jQuery element.
        // Once the fadeIn action is finished a trigger the ``show``
        // event and invoke the optional ``callback``.
        fadeIn: function (options) {
            options || (options = {});
            if (!options.complete) {
                var self = this;
                options.complete = function () {
                    self.show();
                };
            }
            this.elem.fadeIn(options);
        },
        //
        // fadeOut the jQuery element conteining the extension.
        // Once the fadeOut action is finished a trigger the ``hide``
        // event and invoke the optional ``callback``.
        fadeOut: function (options) {
            options || (options = {});
            if (!options.complete) {
                var self = this;
                options.complete = function () {
                    self.hide();
                };
            }
            this.elem.fadeOut(options);
        },
        //
        // Get the skin name for this view
        getSkin: function (prefix) {
            return lux.getSkin(this.elem, prefix || this.className);
        },
        //
        // Set the skin for this view
        setSkin: function (skin, prefix) {
            lux.setSkin(this.elem, skin, prefix || this.className);
        },
        //
        eventName: function (event) {
            var namespace = this.instance_key ? this.instance_key : 'view';
            return event + '.lux.' + namespace;
        },
        //
        enforceFocus: function () {
            var name = this.eventName('focusin'),
                self = this;
            $(document).off(name).on(name, function (e) {
                if (self.elem[0] !== e.target && !self.elem.has(e.target).length)
                    self.elem.trigger('focus');
            });
        },
        //
        // Add a stylesheet to the head tag.
        //
        //  ``rules`` is an array of string with css rules
        //  ``id`` optional id to set in the style tag.
        addStyle: function (rules, id) {
            if (rules.length) {
                var head = $("head"),
                    style;
                if (id) {
                    style = head.find('#' + id);
                    if (!style.length) style = null;
                }
                if (!style) {
                    style = $("<style type='text/css' rel='stylesheet' />"
                        ).appendTo(head).attr('id', id);
                    if (style[0].styleSheet) { // IE
                        style[0].styleSheet.cssText = rules.join("\n");
                    } else {
                        style[0].appendChild(document.createTextNode(rules.join("\n")));
                    }
                }
            }
        },
    });
    //
    //  Create a new View and perform additional action such as:
    //
    //  * Create a jQuery plugin if the ``obj`` has the ``jQuery`` attribute
    //    set to ``true``.
    //  * Register the view for autoloading if the ``selector`` attribute is
    //    available.
    lux.createView = function (name, obj, BaseView) {
        var jQuery = obj.jQuery,
            key = name + '-view';
        delete obj.jQuery;
        //
        obj.name = name;
        obj.instance_key = key;
        BaseView = BaseView || View;
        //
        // Build the new View
        var NewView = BaseView.extend(obj),
            proto = NewView.prototype,
            //
            // view's factory
            create = function (elem, options, render) {
                var view = elem.data(key);
                if (!view) {
                    options || (options = {});
                    if (lux.data_api) {
                        var data = elem.data();
                        _.forEach(data, function(val, key) {
                            if (val === "") data[key] = true;
                        });
                        options = _.extend({}, data, options);
                    }
                    options.elem = elem;
                    view = new NewView(options);
                    if (render) view.render();
                }
                return view;
            };

        NewView.getInstance = function(elem) {
            return elem.data(key);
        };

        if (jQuery) {
            $.fn[name] = function (options) {
                if (options === 'instance') {
                    return this.data(key);
                } else {
                    return create(this, options).elem;
                }
            };
        }

        if (proto.selector) {
            autoViews.push({
                selector: proto.selector,
                load: function (elem) {
                    create($(elem), null, true);
                }
            });
        }
        return NewView;
    };
    //
    //  Load all registered views into ``elem``
    //
    //  If ``elem`` is not provided load registered views into the
    //  whole document.
    lux.loadViews = function (elem) {
        elem = $(elem || document);
        _(autoViews).forEach(function (view) {
            $(view.selector, elem).each(function () {
                view.load(this);
            });
        });
    };

    //
    // Callback for requires
    lux.initWeb = function () {
        $(document).ready(function () {
            var doc = $(this),
                data = doc.find('html').data() || {},
                body = doc.find('body');
            _.extend(lux, data);
            if (lux.debug) {
                logger.config({level: 'debug'});
                if (!logger.handlers.length) {
                    logger.addHandler();
                }
            }
            body.css({opacity: 0});
            try {
                lux.loadViews(doc);
                body.fadeIn(100);
            } finally {
                body.css({opacity: 1});
            }
        });
    };
