

    // Cached regex to split keys for `delegate`.
    var
    //
    delegateEventSplitter = /^(\S+)\s*(.*)$/,
    //
    viewOptions = ['model', 'collection', 'elem', 'id', 'attributes',
                   'className', 'tagName', 'name', 'events'],
    //
    // A view class
    View = lux.View = Class.extend({
        tagName: 'div',

        init: function (options) {
            this.cid = _.uniqueId('view');
            options || (options = {});
            _.extend(this, _.pick(options, viewOptions));
            if (!this.elem) {
                this.setElement($(document.createElement(this.tagName)), false);
            } else {
                this.elem = $(_.result(this, 'elem'));
                this.setElement(this.elem, false);
            }
            if (this.name) this.elem.data(this.name + 'view', this);
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
        jQuery: function () {
            var self = this,
                key = this.name + 'view';
            self.elem.data(key, self);
            //
            $.fn[self.name] = function (options) {
                var view = this.data(key);
                if (!view) {
                    ViewClass = self.prototype.constructor;
                    options.elem = this;
                    view = new ViewClass(options);
                }
                return view.elem;
            };
        }
    });

    //
    // Create a new view and build a jQuery plugin
    lux.createView = function (name, obj, BaseView) {
        var jQuery = obj.jQuery;
        delete obj.jQuery;
        //
        obj.name = name;
        BaseView = BaseView || View;
        //
        // Build the new View
        var NewView = BaseView.extend(obj),
            proto = NewView.prototype,
            key = name + 'view',
            create = function (elem, options, render) {
                var view = elem.data(key);
                if (!view) {
                    if (lux.data_api)
                        options = _.extend({}, elem.data(), options);
                    options.elem = elem;
                    view = new NewView(options);
                    if (render) view.render();
                }
                return view;
            };

        if (jQuery) {
            $.fn[name] = function (options) {
                return create(this, options).elem;
            };
        }

        if (proto.selector) {
            $(document).ready(function () {
                var opts = {};
                $(proto.selector, this).each(function () {
                    create($(this), opts, true);
                });
            });
        }
        return NewView;
    };