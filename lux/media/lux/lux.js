define(['lodash', 'jquery'], function (_, $) {
    "use strict";

    var

    root = window,
    //
    prev_lux = root.lux,
    //
    slice = Array.prototype.slice;
    //
    lux = root.lux = {
        //
        debug: false,
        //
        skins: [],
        //
        // Container of libraries used by lux
        libraries: [],
        //
        media_url: '/media/',
        //
        icon: 'fontawesome',
        //
        data_api: true,
        //
        set_value_hooks: [],
        //
        setValue: function (elem, value) {
            var hook;
            for (var i=0; i<lux.set_value_hooks.length; i++) {
                if (lux.set_value_hooks[i](elem, value)) {
                    return;
                }
            }
            elem.val(value);
        },
        //
        addLib: function (info) {
            if (!_.contains(lux.libraries, info.name)) {
                lux.libraries.push(info);
            }
        },
        //
        // Create a random s4 string
        s4: function () {
            return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
        },
        //
        // Create a UUID4 string
        guid: function () {
            var S4 = lux.s4;
            return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
        },
        //
        isnothing: function (el) {
            return el === undefined || el === null;
        },
        //
        sorted: function (obj, callback) {
            var sortable = [];
            _(obj).forEch(function (elem, name) {
                sortable.push(name);
            });
            sortable.sort();
            _(sortable).forEach(function (name) {
                callback(obj[name], name);
            });
        }
    };

    String.prototype.capitalize = function() {
        return this.charAt(0).toUpperCase() + this.slice(1);
    };

    lux.addLib({name: 'RequireJs', web: 'http://requirejs.org/', version: require.version});
    lux.addLib({name: 'Lo-Dash', web: 'http://lodash.com/', version: _.VERSION});
    lux.addLib({name: 'jQuery', web: 'http://jquery.com/', version: $.fn.jquery});



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
    //  Class
    //  ----------------

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
    }(function() {})),

    //
    // Class With Events
    // requires jQuery loaded
    EventClass = Class.extend({
        //
        // Bind this class to a jQuery element
        bindToElement: function (jElem) {
            this._jquery_element = jElem;
        },
        //
        trigger: function (name, params) {
            if (params) {
                if (!_.isArray(params)) params = [params];
                params.splice(0, 0, this);
            } else {
                params = [this];
            }
            this.jElem().trigger(name, params);
        },
        //
        on: function (name, callback) {
            this.jElem().on(name, callback, slice.call(arguments, 2));
        },
        //
        jElem: function () {
            return this._jquery_element ? this._jquery_element : $(window);
        }
    }),
    //
    // Lux exception:
    //  throw new lux.Exception(message)
    Exception = Class.extend({
        name: 'Exception',
        init: function (message) {
            this.message = message || '';
        },
        toString: function () {
            return this.name + ': ' + this.message;
        }
    }),
    //
    ModelException = Exception.extend({name: 'ModelException'}),
    //
    NotImplementedError = Exception.extend({name: 'NotImplementedError'}),
    //
    // Default values for ``Meta`` attributes.
    default_meta_attributes = {
        'pkname': 'id',
        'name': 'model',
        'defaults': {}
    },
    //
    //  Model Meta
    //  ------------------------

    // Model database meta-class, accessed as ``_meta`` attribute on a ``Model``
    // instance or from the Model.prototype object. It is a placeholder of
    // live instances and it is the interface between a model and backend
    // servers. A ``Meta`` must be registered with a backend before it can
    // use the ``sync`` method. Registration is achieved via the
    // ``set_transport`` method.
    Meta = lux.Meta = Class.extend({
        //
        // Initialisation, set the ``model`` attribute and the attributes
        // for this Meta. The available attributes are the same as
        // ``default_meta_attributes`` object above.
        init: function (model, attrs) {
            this.model = model;
            _.extend(this, attrs);
            this.title = this.title || this.name;
        },
        //
        // Initialise an instance
        init_instance: function (o, fields) {
            o._fields = {};
            o._changed = {};
            o.cid = _.uniqueId('model');
            if (fields === Object(fields)) {
                _(fields).forEach(function (field, name) {
                    this.set_field(o, name, field, true);
                }, this);
            }
        },
        //
        // Fetch a bunch of ids from the backend server
        get: function (ids, options) {
            if (this._backend) {
                if (!options) {
                    options = {};
                }
                if (!$.isArray(ids)) {
                    ids = [ids];
                }
                var crud = {},
                    meta = this;
                _(ids).forEach(function (id) {
                    meta._add_to_crud(crud, 'read', id, options);
                });
                meta._backend.send(crud.read);
            } else {
                throw new ModelException('Cannot sync ' + this + '. No backend registered.');
            }
        },
        //
        // update live data with information from the server
        update: function (data) {
            var self = this,
                all = [],
                instance;
            _(data).forEach(function (o) {
                var instance = self.liveStorage.getItem(o.id);
                if (instance) {
                    instance.update(o.fields);
                    // reset the changed object
                    instance._changed = {};
                } else {
                    instance = new self.model(o.fields);
                }
                all.push(instance);
            });
            return all;
        },
        //
        // Set a new value for a field.
        // It returns a value different from undefined
        // only when the field has changed
        set_field: function (instance, field, value, initialising) {
            if (value === undefined) return;
            // Check if there is a validater for the field
            if (this.fields) {
                var f = this.fields[field];
                if (f) {
                    value = f.validate(instance, value);
                } else if (f === null) {
                    instance[field] = value;
                    return;
                }
            }
            if (initialising) {
                instance._fields[field] = value;
            } else {
                var prev = instance.get(field);
                if (_.isEqual(value, prev)) return;
                instance._fields[field] = value;
                return prev === undefined ? null : prev;
            }
        },
        //
        toString: function () {
            return this.name;
        }
    }),
    //
    // Metaclass for models
    // --------------------------------

    // Override the standard ``Type`` so that the new model class
    // contains the ``_meta`` attribute, and instance of ``Meta``.
    ModelType = lux.ModelType = Type.extend({
        //
        new_class: function (Prototype, attrs) {
            attrs || (attrs = {});
            var meta = Prototype._meta,
                mattrs = _.merge({}, default_meta_attributes, attrs.meta);
            // Make sure we inherit fields for parent models
            if (meta && meta.fields) {
                mattrs.fields = this.mergeFields([meta.fields, mattrs.fields]);
            }
            var cls = this._super(Prototype, attrs);
            cls._meta = cls.prototype._meta = new Meta(cls, mattrs);
            return cls;
        },
        //
        mergeFields: function (groups) {
            var map = {},
                list = [],
                merged = [];
            _(groups).forEach(function (fields) {
                _(fields).forEach(function (field) {
                    if (map[field.name]) {
                        map[field.name] = field;
                    } else {
                        map[field.name] = field;
                        list.push(field.name);
                    }
                });
            });
            _(list).forEach(function (name) {
                merged.push(map[name]);
            });
            return merged;
        }
    }),
    //
    // Model
    // --------------------------
    //
    // The base class for a model. A model is a single, definitive source
    // of data about your data. A Model consists of ``fields`` and behaviours
    // of the data you are storing.
    Model = lux.Model = EventClass.extend({
        // Model uses a specialised metaclass
        Metaclass: ModelType,
        //
        init: function (data) {
            this._meta.init_instance(this, data);
        },
        //
        // Primary key value. If the model is not persistent (not in ``sync`` with
        // the backend) it can be undefined.
        pk: function () {
            return this.get(this._meta.pkname);
        },
        // Has this model been saved to the server yet? If the model does
        // not yet have a pk value, it is considered to be new.
        isNew: function () {
            return this.pk() ? false : true;
        },
        //
        isDeleted: function () {
            return this._deleted === true;
        },
        //
        // Object containing all fields for this model instance
        fields: function () {
            return this._fields;
        },
        //
        // Return a shallow copy of the model's attributes for JSON
        // stringification.
        // This can be used for persistence, serialization, or for augmentation
        // before being sent to the server.
        // If ``changed`` is ``true`` it returnes only fields which
        // have changed if the model is already persistent.
        toJSON: function (changed) {
            var data = {},
                fields = this._fields,
                all = fields;
            if (changed && !this.isNew()) all = this._changed;
            _(all).forEach(function (value, name) {
                value = fields[name];
                if (value instanceof Date) {
                    data[name] = 0.001*value.getTime();
                } else {
                    data[name] = value;
                }
            });
            return data;
        },
        //
        // Set a field value
        set: function (field, value) {
            var prev = this._meta.set_field(this, field, value);
            if (prev !== undefined) {
                this._changed[field] = prev;
                this.trigger('change', [this, field]);
            }
        },
        //
        changedFields: function (fields) {
            if (!fields) {
                return this._changed;
            } else if (typeof(fields) === 'string') {
                return this._changed[fields];
            } else {
                return this._changed;
            }
        },
        //
        hasChanged: function () {
            return _.size(this._changed) > 0;
        },
        //
        previous: function (field) {
            return this._changed[field];
        },
        //
        // get a field value
        get: function (field) {
            return this._fields[field];
        },
        //
        // Update fields with new values
        update: function (fields) {
            if (fields === Object(fields)) {
                var self = this;
                _(fields).forEach(function (value, name) {
                    self.set(name, value);
                });
            }
        },
        //
        'delete': function () {
            this._deleted = true;
        },
        //
        // Sync a model
        sync: function (store, options) {
            options || (options = {});
            var callback = options.success,
                info = this._sync_data(options),
                self = this;
            if (info) {
                info.model = this._meta.name;
                info.success = function (data, status, response) {
                    self.sync_callback(data, status, response);
                    if (callback) callback(self);
                };
                return store.execute(info);
            } else if (callback) {
                callback(self);
            }
        },
        //
        // Calledback after a ``sync`` has terminated with success
        // Override  if you need to
        sync_callback: function (data, status, response) {
            if (response.status === 200 || response.status === 201) {
                this._changed = {};
                this.update(data);
            } else if (response.crud === Crud.delete) {
                this.trigger('deleted');
            } else {
                logger.warning('Could not understand response');
            }
        },
        //
        toString: function () {
            return this._meta.name + '-' + this.cid;
        },
        //
        // Get a jQuery form element for this model.
        get_form: function () {},
        //
        // Update the input/select elements in a jQuery form element with data
        // from the model
        update_form: function (form) {
            _(this.fields()).forEach(function (val, name) {
                var elem = form.find("[name=" + name + "]");
                if (elem.length) {
                    lux.set_value(elem, val);
                }
            });
        },
        //
        // Replace fields with a new set
        // If available fields are not present in ``new_fields``, they will be
        // removed
        replace: function (new_fields) {
            var self = this;
            //
            _(this._fields).forEach(function (value, name) {
                if (new_fields[name] === undefined) {
                    delete self._fields[name];
                    self.trigger('change', name);
                }
            });
            this.update(new_fields);
        },
        //
        //  Private method which return serialised representation of model
        //  data for synchronisation with backend store.
        //  It returns an object containing:
        //
        //  * ``crud`` - the CRUD action to perform (``create``, ``update`` or ``delete``)
        //  * ``item`` - object containg the following entries
        //    * ``pk`` primary key (not available for ``create`` action)
        //    * ``fields`` - object with model fields (not available for ``delete`` action)
        //    * ``cid`` - custom identifier
        _sync_data: function (options) {
            options || (options = {});
            var pkvalue = this.pk();
            if (this.isDeleted() && pkvalue) {
                // DELETE THE MODEL
                options.crud = Crud.delete;
                options.item = {
                    pk: pkvalue
                };
            } else if (pkvalue && this.hasChanged()) {
                // UPDATE THE MODEL
                options.crud = Crud.update;
                options.item = {
                    pk: pkvalue,
                    data: this.toJSON()
                };
            } else if (!pkvalue) {
                // CREATE A NEW MODEL
                var o = this.toJSON();
                if (_.size(o)) {
                    options.crud = Crud.create;
                    options.item = {data: o};
                } else {
                    return;
                }
            } else {
                return;
            }
            return options;
        }
    }),

    //  Collection of Models
    //  -------------------------

    //  A collection maintain an ordered group of model instances
    Collection = lux.Collection = Class.extend({
        //
        init: function (model, store) {
            var self = this,
                _data = [],
                _map = {},
                NewModel = self.model = model || Model.extend({});
            self.store = create_store(store);


            Object.defineProperty(self, 'length', {
                get: function () {
                    return _data.length;
                }
            });
            //
            _.extend(self, {

                // Get a model from a collection, specified by index
                at: function (index) {
                    var id = _data[index];
                    if (id) return _map[id];
                },
                //
                // Get a model from a collection, specified by an id
                get: function (id) {
                    return _map[id];
                },
                //
                // Add a model (or an array of models) to the collection,
                // firing an "add" event.
                //
                // * Can pass raw attributes objects, and have them be
                //   vivified as instances of the model.
                // * Returns the added (or preexisting, if duplicate) models.
                // *  Pass {at: index} to splice the model into the collection at
                //    the specified index.
                // * If you're adding models to the collection that are already
                //   in the collection, they'll be ignored, unless you pass
                //   ``{merge: true}``, in which case their attributes will
                //   be merged into the corresponding models, firing any
                //   appropriate "change" events.
                add: function (data, options) {
                    var models = [],
                        existing;
                    //
                    options || (options = {});
                    if (!_.isArray(data)) {
                        data = [data];
                    }
                    //
                    _(data).forEach(function (o) {
                        if (!(o instanceof NewModel)) {
                            o = new NewModel(o);
                        }
                        existing = _map[o.cid];
                        if (existing) {
                            if (options.merge) {
                                existing.update(o.fields());
                                if (existing.hasChanged()) {
                                    models.push(existing);
                                }
                            }
                        } else {
                            _map[o.cid] = o;
                            _data.push(o.cid);
                            models.push(o);
                        }
                    });
                    return models;
                },
                //
                set: function (models) {
                    _(models).forEach(function (model) {
                        var id = model.id(),
                            existing = _map[id];
                        if (existing) {
                            existing.update(model.fields());
                        } else {
                            _map[id] = model;
                            _data.push(id);
                        }
                    });
                },
                //
                // Clear the collection
                clear: function () {
                    _data = [];
                    _map = {};
                },
                //
                //
                forEach: function (callback) {
                    var len = _data.length,
                        res;
                    for (var i=0; i<len; i++) {
                        if(callback(_map[_data[i]], i) === false) break;
                    }
                },
                //
                each: function (callback) {
                    self.forEach(callback);
                }
            });
        },
        //
        reset: function (models) {
            this.clear();
            this.set(models);
        },
        //
        //
        // Fetch a new Collection of models from the store
        fetch: function (options) {
            options || (options = {});
            var self = this;
            if (!options.success) {
                options.success || function (data) {
                    data = self.parse(data);
                    self.reset(data);
                };
            }
            options.meta = this.model._meta;
            self.store.execute(options);
        },
        //
        //  Commit changes to backend store
        sync: function (options) {
            options || (options = {});
            var self = this,
                store = this.store,
                groups = {},
                callback = options.success,
                errback = options.error,
                group, item;

            this.forEach(function (model) {
                model.sync(store, options);
            });
        },
        //
        // Parse data into a collection of models
        parse: function (data) {
            return data;
        },
        //
        toString: function () {
            return this.model._meta.name + '[' + this.length + ']';
        },
        //
        afterSync: function (op, data) {
            if (op === Crud.delete) {

            } else if (op === Crud.create) {
            } else if (op === Crud.update) {
            }
        }
    });



    lux.EventClass = EventClass;
    lux.Exception = Exception;
    lux.ModelException = ModelException;
    lux.NotImplementedError = NotImplementedError;

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
        tagName: 'div',
        //
        defaults: null,
        //
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
                        style[0].styleSheet.cssText = rules.join(" ");
                    } else {
                        style[0].appendChild(document.createTextNode(rules.join(" ")));
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

    //
    //  Lux Logger
    //  --------------------

    // Usage:
    //
    //      logger = new Logger();
    //      logger.info('info message')
    var
    log_mapping = {
        'debug': 10,
        'info': 20,
        'warning': 30,
        'error': 40,
        'critical': 50
    },
    //
    default_level = 'info',
    //
    Logger = lux.Logger = Class.extend({
        //
        init: function (opts, parent) {
            var self = this,
                //
                // children for this logger
                children = {},
                //
                // config object
                config = {
                    level: default_level,
                    //
                    formatter: function (msg, level) {
                        return level + ': ' + msg;
                    }
                };

            // Logging shortcut methods
            _(log_mapping).forEach(function (n, level) {
                //
                self[level] = function (msg) {
                    self.log(msg, level);
                };
            });

            _.extend(self, {
                handlers: [],
                //
                config: function (opts) {
                    opts = Object(opts);
                    if (opts.level && log_mapping[opts.level]) {
                        config.level = opts.level;
                    }
                    return config;
                },
                //
                getConfig: function () {
                    return config;
                },
                //
                log: function (msg, level) {
                    var nlevel = log_mapping[level] || 0;
                    if (nlevel > log_mapping[config.level]) {
                        var handlers = self.getHandlers(),
                            hnd;

                        for (var i=0; i<handlers.length; i++) {
                            hnd = handlers[i];
                            if (nlevel >= hnd.nlevel) hnd.log(msg, level);
                        }
                    }
                },
                //
                get: function (name) {
                    var log = children[name];
                    if (!log) {
                        log = new Logger({namespace: name}, self);
                        children[name] = log;
                    }
                    return log;
                },
                //
                getHandlers: function () {
                    if (!self.handlers.length && parent) {
                        return parent.getHandlers();
                    } else {
                        return self.handlers;
                    }
                }
            });
            //
            self.config(opts);
        },
        //
        addHandler: function(options, handler) {
            handler = handler || new LogHandler();
            handler.config(_.extend({}, this.getConfig(), options));
            this.handlers.push(handler);
        }
    }),
    //
    //  Default LogHandler
    //  ---------------------------
    //
    //  Logs messages to the console
    LogHandler = lux.LogHandler = Class.extend({

        config: function (options) {
            _.extend(this, options);
            this.nlevel = log_mapping[this.level] || 0;
        },
        //
        log: function(msg, level) {
            console.log(this.formatter(msg, level));
        }
    }),
    //
    //  HTML LogHandler
    //  ---------------------------
    //
    //  Logs messages to an HTML element
    HtmlHandler = lux.HtmlLogHandler = LogHandler.extend({
        //
        init: function (elem) {
            this.elem = $(elem);
            this.elem.addClass('lux-logger');
        },
        //
        log: function(msg, level) {
            msg = this.formatter(msg, level);
            msg = '<pre class="' + level + '">' + msg + '</pre>';
            this.elem.prepend(msg);
        }
    });
    //
    //  Create the root logger
    var logger = new Logger();
    //
    lux.getLogger = function (namespace, options) {
        var log = logger;
        if (namespace) {
            _.each(namespace.split('.'), function (name) {
                log = log.get(name);
            });
        }
        if (options) {
            log.config(options);
        }
        return log;
    };
    //
    var
    // CRUD actions
    Crud = {
        create: 'create',
        read: 'read',
        update: 'update',
        'delete': 'delete',
    },
    CrudMethod = lux.CrudMethod = {
        create: 'POST',
        read: 'GET',
        update: 'PUT',
        destroy: 'DELETE'
    },
    //
    stores = {},
    //
    register_store = lux.register_store = function (scheme, Store) {
        stores[scheme] = Store;
    },
    //
    // Create a new Backend Store from a ``store`` url
    //
    create_store = lux.create_store = function (store, options) {
        if (store instanceof Backend) {
            return store;
        } else if (_.isString(store)) {
            var idx = store.search('://'),
                scheme = idx === -1 ? 'http' : store.substr(0, idx),
                Store = stores[scheme];
            if (Store && store)
                return new Store(store, options, scheme);
        }
        // A dummy backend
        return new Backend(store, options, 'dummy');
    };
    //
    // Base class for backends to use when synchronising Models
    //
    // Usage::
    //
    //      backend = lux.Socket('ws://...')
    var Backend = lux.Backend = lux.Class.extend({
        //
        options: {
            dataType: 'json'
        },
        //
        init: function (url, options, type) {
            this.type = type;
            this.url = url;
            this.options = _.merge({}, this.options, options);
        },
        //
        // The synchoronisation method
        //
        // It has an API which match jQuery.ajax method
        //
        // Available options entries:
        // * ``beforeSend`` A pre-request callback function that can be used to
        //   modify the object before it is sent. Returning false will cancel the
        //   execution.
        // * ``error`` callback invoked if the execution fails
        // * ``meta`` optional Model metadata
        // * ``model`` optional Model instance
        // * ``success`` callback invoked on a successful execution
        // * ``type`` the type of CRUD operation
        execute: function (options) {
            if (options.success) {
                options.success([]);
            }
        },
        //
        toString: function () {
            return this.type + ' ' + this.url;
        }
    });

    //  AJAX Backend
    //  -------------------------
    //
    //  Uses jQuery.ajax method to execute CRUD operations
    var AjaxBackend = lux.Backend.extend({
        //
        init: function (url, options, type) {
            this._super(url, options, 'ajax');
        },
        //
        // The ajax execute method for single model or group of models
        execute: function (options) {
            var url = this.url,
                model = options.model,
                item = options.item;
            delete options.model;
            //
            options.type = lux.CrudMethod[options.crud] || options.type || 'GET';
            //
            // If a model is given, this is an operation on a single instance
            if (item) {
                delete options.item;
                // primary key given, change url
                if (item.pk) url = lux.utils.urljoin(url, item.pk);
                options.data = item.data;
            }
            $.ajax(url, options);
        }
    });
    //
    register_store('http', AjaxBackend);
    register_store('https', AjaxBackend);

    //
    //  WebSocket Backend
    //  ----------------------------------------
    //
    //  Uses lux websocket CRUD protocol
    var Socket = lux.Backend.extend({
        //
        options: {
            resource: null,
            reconnecting: 1,
            hartbeat: 5,
            maxDelay: 3600,
            maxRetries: null,
            factor: 2.7182818284590451, // (e)
            jitters: 0,
            jitter: 0.11962656472
        },
        //
        init: function (url, options, type) {
            var self = this;
            url = this.websocket_uri(url);
            this._super(url, options, 'websocket');
            this._retries = 0;
            this._transport = null;
            this._opened = false;
            this._pending_messages = {};
            this._delay = this.options.reconnecting;
            this._queue = [];
            self.connect();
        },
        //
        opened: function () {
            return this._opened;
        },
        //
        // Connect the websocket
        // This method can be called several times by the
        // reconnect method (reconnecting must be positive).
        connect: function () {
            var options = this.options,
                uri = this.url,
                self = this;
            if (options.resource) {
                uri += options.resource;
            }
            logger.info('Connecting with ' + self);
            this._transport = new WebSocket(uri);
            this._transport.onopen = function (e) {
                self.onopen();
            };
            this._transport.onmessage = function (e) {
                if (e.type === 'message') {
                    self.onmessage(e);
                }
            };
            this._transport.onclose = function (e) {
                self.onclose();
            };
        },
        //
        onopen: function () {
            this._opened = true;
            logger.info(this + ' opened.');
            if (this.options.onopen) {
                this.options.onopen.call(this);
            }
            if (this._queue) {
                var queue = this._queue;
                this._queue = [];
                _(queue).forEach(function (msg) {
                    this._transport.send(msg);
                }, this);
            }
        },
        //
        reconnect: function () {
            var o = this.options,
                self = this;
            if (!this._delay) {
                web.logger.info('Exiting websocket');
                return;
            }
            this._retries += 1;
            if (o.maxRetries !== null && (this._retries > o.maxRetries)) {
                web.logger.info('Exiting websocket after ' + this.retries + ' retries.');
                return;
            }
            //
            this._delay = Math.min(this._delay * o.factor, o.maxDelay);
            if (o.jitter) {
                this._delay = lux.math.normalvariate(this._delay, this._delay * o.jitter);
            }
            //
            web.logger.info('Try to reconnect websocket in ' + this._delay + ' seconds');
            this.trigger('reconnecting', this._delay);
            this._reconnect = lux.eventloop.call_later(this._delay, function () {
                self._reconnect = null;
                self.connect();
            });
        },
        //
        // Send a set of operations to the backend
        // If ``options`` contains the ``item`` entry, than it is converted into
        // a sinle ``data`` entry ``options.data = [options.item]``
        execute: function (options) {
            if (options.beforeSend && options.beforeSend.call(options, this) === false) {
                // Don't send anything, simply return
                return;
            }
            //
            var obj = {
                // new message id
                mid: this.new_mid(options),
                action: options.action || lux.CrudMethod[options.crud] || options.crud,
                model: options.model
            };
            //
            // This is an execution for a single item
            if (options.item) {
                _.extend(obj, options.item);
            } else {
                obj.data = options.data;
            }
            obj = JSON.stringify(obj);
            if (this._opened) {
                this._transport.send(obj);
            } else {
                this._queue.push(obj);
            }
        },
        //
        // Handle incoming messages
        onmessage: function (e) {
            var obj = JSON.parse(e.data),
                mid = obj.mid,
                options = mid ? this._pending_messages[mid] : undefined,
                data = obj.data;
            obj.response = e;
            obj.backend = this;
            if (options) {
                delete this._pending_messages[mid];
            }
            if (obj.error) {
                if (options && options.error) {
                    options.error(obj, 'error', obj.error);
                } else {
                    logger.error(this.toString() + ' - ' + obj.error);
                }
            } else {
                if (options && options.success) {
                    options.success(data, 'success', obj);
                } else {
                    logger.warning(
                        this.toString() + ' - Got message with no callback registered');
                }
            }
        },
        //
        // The socket is closed
        // If enabled, it auto-reconnects with an exponential back-off
        onclose: function () {
            this._opened = false;
            logger.warning(this + ' closed.');
            this.reconnect();
        },
        //
        // Create a new message id and add the options object to the
        // pending messages object
        new_mid: function (options) {
            if (options.success || options.error) {
                var mid = _.uniqueId('ws-message');
                this._pending_messages[mid] = options;
                return mid;
            }
        },
        //
        websocket_uri: function (url) {
            var loc = window.location;
            if (!url) {
                url = loc.href.split('?')[0];
            }
            if (url.substring(0, 7) === 'http://') {
                return 'ws://' + url.substring(7);
            } else if (url.substring(0, 8) === 'https://') {
                return 'wss://' + url.substring(8);
            } else {
                if (url.substring(0, 5) === 'ws://' || url.substring(0, 6) === 'wss://') {
                    return url;
                } else {
                    var protocol = loc.protocol === 'http:' ? 'ws:' : 'wss:';
                    return lux.utils.urljoin(protocol, loc.host, loc.pathname, url);
                }
            }
        }
    });
    //
    register_store('ws', Socket);
    register_store('wss', Socket);
    //
    var ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

    //
    //  Convert a number into a letter representation
    //
    //  num_to_letter(1) == 'A'
    //  num_to_letter(2) == 'B'
    //  num_to_letter(27) == 'AA'
    lux.num_to_letter = function (num) {
        var len = ALPHABET.length,
            s = '';
        while (num >= len) {
            var rem = num % len;
            num = Math.floor(num/len);
            s += ALPHABET[rem];
        }
        s += ALPHABET[num];
        return s;
    };

    lux.fields_from_array = function (arr) {
        var fields = {};
        _(arr).forEach(function (f) {
            var values = fields[f.name];
            if (values === undefined) {
                fields[f.name] = f.value;
            } else if(_.isArray(values)) {
                values.push(f.value);
            } else {
                fields[f.name] = [values, f.value];
            }
        });
        return fields;
    };
    //
    // An object which remember insertion order:
    //
    //  var o = new lux.Ordered();
    //  o.set('foo', 4);
    //  o.set('bla', 3);
    //  o.order === ['foo', 'bla'];
    lux.Ordered = Class.extend({
        init: function () {
            this.all = {};
            this.order = [];
        },
        set: function (key, obj) {
            if (this.all[key]) {
                this.all[key] = obj;
            } else if (key) {
                this.order.push(key);
                this.all[key] = obj;
            }
        },
        get: function (key) {
            return this.all[key];
        },
        at: function (index) {
            if (index < this.order.length) return this.all[this.order[index]];
        },
        size: function () {
            return this.order.length;
        },
        each: function (iterator, context) {
            _(this.order).forEach(function (key, index) {
                iterator.call(context, this.all[key], key, index);
            }, this);
        },
        ordered: function () {
            var all = [];
            _(this.order).forEach(function (key) {
                all.push(this.all[key]);
            }, this);
            return all;
        }
    });

    /** SkipList
    *
    * Task: JavaScript implementation of a skiplist
    *
    * A skiplist is a randomized variant of an ordered linked list with
    * additional, parallel lists.  Parallel lists at higher levels skip
    * geometrically more items.  Searching begins at the highest level, to quickly
    * get to the right part of the list, then uses progressively lower level
    * lists. A new item is added by randomly selecting a level, then inserting it
    * in order in the lists for that and all lower levels. With enough levels,
    * searching is O( log n).
    *
    */
    var SKIPLIST_MAXLEVELS = 32;

    function SLNode(key, value, next, width) {
        this.key = key;
        this.value = value;
        this.next = next;
        this.width = width;
    }

    var SkipList = lux.SkipList = function (maxLevels, unique) {
        // Properties
        maxLevels = Math.min(SKIPLIST_MAXLEVELS,
                Math.max(8, maxLevels ? maxLevels : SKIPLIST_MAXLEVELS));
        //
        var array = function (val) {
            var a = [],
                c = maxLevels;
            while(c--) {
                a.push(val);
            }
            return a;
        };
        //
        var log2 = Math.log(2),
            size = 0,
            head = new SLNode('HEAD', null, new Array(maxLevels), array(1)),
            level = 1,
            i;

        Object.defineProperty(this, 'length', {
            get: function () {
                return size;
            }
        });

        Object.defineProperty(this, 'levels', {
            get: function () {
                return levels;
            }
        });

        _.extend(this, {
            insert: function(key, value) {
                var chain = new Array(maxLevels),
                    rank = array(0),
                    node = head,
                    prevnode,
                    steps;
                for(i=level-1; i>=0; i--) {
                    // store rank that is crossed to reach the insert position
                    rank[i] = i === level-1 ? 0 : rank[i+1];
                    while (node.next[i] && node.next[i].key <= key) {
                        rank[i] += node.width[i];
                        node = node.next[i];
                    }
                    chain[i] = node;
                }
                // The key already exists
                if (chain[0].key === key && unique) {
                    return size;
                }
                //
                var lev = Math.min(maxLevels, 1 -
                    Math.round(Math.log(Math.random())/log2));
                if (lev > level) {
                    for (i = level; i < lev; i++) {
                        rank[i] = 0;
                        chain[i] = head;
                        chain[i].width[i] = size;
                    }
                    level = lev;
                }
                //
                // create new node
                node = new SLNode(key, value, new Array(maxLevels),
                    new Array(maxLevels));
                for (i = 0; i < lev; i++) {
                    prevnode = chain[i];
                    steps = rank[0] - rank[i];
                    node.next[i] = prevnode.next[i];
                    node.width[i] = prevnode.width[i] - steps;
                    prevnode.next[i] = node;
                    prevnode.width[i] = steps + 1;
                }

                // increment width for untouched levels
                for (i = lev; i < level; i++) {
                    chain[i].width[i] += 1;
                }

                size += 1;
                return size;
            },
            //
            forEach: function (callback) {
                var node = head.next[0];
                while (node) {
                    callback(node.value, node.score);
                    node = node.next[0];
                }
            }
        });
    };




    var icons = lux.icons = {
        //
        fontawesome: function (elem, options) {
            var i = $('i', elem).remove(),
                ni = '<i class="fa fa-' + options.icon + '"></i>';
            if (elem[0].text) {
                elem[0].text = ' ' + elem[0].text;
            }
            elem.prepend(ni);
        }
    };

    lux.addIcon = function (elem, options) {
        var p = lux.icons[lux.icon];
        if (p && !elem.is('html')) {
            if (!options) options = elem.data();
            if (options.icon) p(elem, options);
        }
    };

    lux.autoViews.push({
        selector: '[data-icon]',
        load: function(elem) {
            lux.addIcon($(elem));
        }
    });

    var
    //
    BUTTON_SIZES = ['large', 'normal', 'small', 'mini'],
    //
    buttonGroup = lux.buttonGroup = function (options) {
        options || (options = {});
        var elem = $(document.createElement('div'));
        if (options.vertical) elem.addClass('btn-group-vertical');
        else elem.addClass('btn-group');
        if (options.radio) {
            elem.data('toggle', 'buttons-radio');
        }
        return elem;
    },
    //
    Button = lux.Button = lux.createView('button', {
        //
        tagName: 'button',
        //
        selector: '.btn',
        //
        defaults: {
            skin: 'default'
        },
        //
        className: 'btn',
        //
        initialise: function (options) {
            var btn = this.elem;
            btn.addClass(this.className).attr({
                type: options.type,
                title: options.title,
                href: options.href,
            }).addClass(options.classes);
            //
            this.setSkin(options.skin);
            this.setSize(options.size);
            if (options.text) btn.html(options.text);
            if (options.icon) lux.addIcon(btn, options);
            if (options.block) btn.addClass('btn-block');
        },
        //
        setSize: function (size) {
            if(BUTTON_SIZES.indexOf(size) > -1) {
                var elem = this.elem,
                    prefix = this.className + '-';
                _(BUTTON_SIZES).forEach(function (size) {
                    elem.removeClass(prefix + size);
                });
                elem.addClass(prefix + size);
            }
        }
    });

    var
    //
    // Form view
    Form = lux.Form = lux.createView('form', {
        //
        tagName: 'form',
        //
        defaults: {
            dataType: "json",
            layout: null,
            groupClass: 'form-group',
            controlClass: 'form-control',
            skin: 'default',
            ajax: false,
            complete: null,
            error: null,
            success: null
        },
        //
        initialise: function (options) {
            this.options = options;
            if (this.elem.hasClass('horizontal')) {
                options.layout = 'horizontal';
            } else if (this.elem.hasClass('inline')) {
                options.layout = 'inline';
            }
            if (options.layout)
                this.elem.addClass('form-' + options.layout);
            lux.setSkin(this.elem, options.skin);
        },
        //
        // Add a list of ``Fields`` to this form.
        addFields: function (fields) {
            var processed = [],
                self = this,
                elem,
                fieldset;
            //
            _(fields).forEach(function (field) {
                if (field && field.name && processed.indexOf(field.name) === -1) {
                    processed.push(field.name);
                    field.render(self);
                }
            });
            return this;
        },
        //
        // Add a submit button
        addSubmit: function (options) {
            options || (options = {});
            if (!options.skin) options.skin = this.options.skin;
            if (!options.tagName) {
                options.tagName = 'button';
                if (!options.text) options.text = 'Submit';
            }
            var btn = new Button(options);
            this.elem.append(btn.elem);
        },
        //
        render: function () {
            if (this.options.layout) {
                var layout = this['render_' + this.options.layout];
                layout.call(this);
            } else {
                var self = this;
                $('input,select,textarea', this.elem).each(function () {
                    var elem = $(this);
                    if (elem.attr('type') !== 'checkbox') {
                        elem.addClass(self.options.controlClass);
                    }
                });
            }
            return this;
        },
        //
        //
        render_horizontal: function () {
            var self = this,
                elem, label, parent, wrap, group;
            $('input,select,textarea', this.elem).each(function () {
                elem = $(this).addClass(self.options.controlClass);
                wrap = elem.closest(self.options.groupClass);
                if (wrap.length) {
                    parent = elem.parent();
                    if (!parent.is('label')) parent = elem;
                    wrap = $(document.createElement('div')).addClass('controls');
                    parent.before(wrap).appendTo(wrap);
                    group = wrap.parent();
                    if (!wrap.hasClass('control-group')) {
                        label = wrap.prev();
                        group = $(document.createElement('div')).addClass('control-group');
                        wrap.before(group).appendTo(group);
                        if (label.is('label')) {
                            group.prepend(label.addClass('control-label'));
                        }
                    }
                }
            });
        },
        //
        fieldset: function (fieldset_selector) {
            var fieldsets = this.elem.children('fieldset'),
                fieldset;
            //
            // Find the appropiate fieldset
            if (fieldset_selector) {
                if (fieldset_selector instanceof jQuery) {
                    fs = fieldset_selector;
                } else if (fieldset_selector instanceof HTMLElement) {
                    fs = $(fieldset_selector);
                } else if (fieldset_selector.id) {
                    fs = this.elem.find('#' + fieldset_selector.id);
                } else if (fieldset_selector.Class) {
                    fs = this.elem.find('.' + fieldset_selector.Class);
                } else {
                    fs = fieldsets.last();
                }
                if (fs.length) {
                    fieldset = fs;
                } else {
                    fieldset = $(document.createElement('fieldset')).appendTo(this.elem);
                    if (fieldset_selector.id) {
                        fieldset.attr(id, fieldset_selector.id);
                    } else if (fieldset_selector.Class) {
                        fieldset.addClass(fieldset_selector.Class);
                    }
                }
            } else if (!fieldsets.length) {
                fieldset = $(document.createElement('fieldset')).appendTo(this.elem);
            } else {
                fieldset = fieldsets.first();
            }
            return fieldset;
        }
    }),
    //
    //  Base class for ``Form`` fields
    Field = lux.Field = lux.Class.extend({
        fieldOptions: [
            'tagName', 'type', 'label', 'placeholder', 'autocomplete',
            'required', 'fieldset'],
        //
        tagName: 'input',
        //
        type: 'text',
        //
        init: function (name, options) {
            options || (options = {});
            this.name = name;
            _.extend(this, _.pick(options, this.fieldOptions));
            this.label = this.label || this.name.capitalize();
            if (this.required) this.required = 'required';
        },
        //
        validate: function (model, value) {
            if (value || value === 0) return value + '';
        },
        //
        setValue: function (model, elem) {
            if (model) elem.val(model.get(this.name));
        },
        //
        // Render this field for the ``form``.
        // Return a jQuery element which can be included in the ``form``.
        render: function (form) {
            var
            elem = $(document.createElement(this.tagName)).attr({
                name: this.name,
                type: this.type,
                title: this.title || this.name,
                autocomplete: this.autocomplete,
                placeholder: this.getPlaceholder()
            });
            this.setValue(form.model, elem);
            form.elem.append(this.outerContainer(elem, form));
        },
        //
        getPlaceholder: function () {
            if (this.placeholder !== false)
                return this.placeholder ? this.placeholder : this.label;
        },
        //
        // Wrap field and label with an outer container ``div.groupClass``.
        outerContainer: function (elem, form) {
            if (form.layout !== 'inline') {
                var id = elem.attr('id');
                if (!id) {
                    id = _.uniqueId('field');
                    elem.attr('id', id);
                }
                //
                var label = $(document.createElement('label')).html(this.label
                        ).attr('for', id),
                    outer = $(document.createElement('div')).addClass(
                        form.options.groupClass);
                return outer.append(label).append(elem);
            } else {
                return elem;
            }
        }
    }),
    //
    IntegerField = lux.Field = Field.extend({
        type: 'number',
        //
        validate: function (model, value) {
            return parseInt(value, 10);
        }
    }),
    //
    FloatField = lux.FloatField = Field.extend({
        type: 'number',
        //
        validate: function (model, value) {
            return parseFloat(value);
        }
    }),
    //
    BooleanField = lux.BooleanField = Field.extend({
        type: 'checkbox',
        //
        setValue: function (model, elem) {
            if (model) {
                var val = model.get(this.name) ? true : false;
                elem.prop('checked', val);
            }
        },
        //
        validate: function (model, value) {
            if (value !== undefined)
                return value === true || value === 'on';
        },
        //
        //
        render: function (form) {
            var elem = $(document.createElement(this.tagName)).attr({
                name: this.name,
                type: this.type,
                title: this.title
            });
            this.setValue(form.model, elem);
            var label = $(document.createElement('label')),
                outer = $(document.createElement('div')).addClass('checkbox');
            elem = outer.append(label.append(elem).append(this.label));
            form.elem.append(elem);
        },
    }),
    //
    // A ``ChoiceField`` is by default rendered as a ``select`` element.
    ChoiceField = lux.ChoiceField = Field.extend({
        //
        // If the ``select`` dictionary is passed and the ``tagName`` is ``select``
        // the jQuery select plugin is applied.
        fieldOptions: _.union(
            Field.prototype.fieldOptions,
            ['choices', 'select2']),
        //
        tagName: 'select',
        //
        type: null,
        //
        setValue: function (model, elem) {
            if (model) {
                var val = model.get(this.name);
                if (elem.is('select')) {
                } else if (elem.val() === val) {
                    elem.prop('checked', true);
                }
            }
        },
        //
        render: function (form) {
            var self = this,
                choices= this.choices,
                elem, text;
            if (_.isFunction(choices)) choices=  choices();
            //
            // Select element
            if (this.tagName === 'select') {
                elem = $(document.createElement(this.tagName)).attr({
                    name: this.name
                }).append($("<option></option>"));
                //
                _(choices).forEach(function (val) {
                    if (_.isString(val)) text = val;
                    else {
                        text = val.text || val.value;
                        val = val.value;
                    }
                    elem.append($("<option></option>").val(val).text(text));
                });
                self.setValue(form.model, elem);
                form.elem.append(self.outerContainer(elem, form));
                if (this.select2) {
                    var opts = this.select2;
                    if (!opts.placeholder) opts.placeholder = this.getPlaceholder();
                    elem.Select(opts);
                }
            //
            // Radio element
            } else if (this.tagName === 'input' && this.type === 'radio') {
                _(choices).forEach(function (val) {
                    if (val instanceof string) text = val;
                    else {
                        text = val.text || val.value;
                        val = val.value;
                    }
                    elem = $(document.createElement(this.tagName)).attr({
                        type: 'radio',
                        name: self.name,
                        value: val
                    }).html(text);
                    self.setValue(form.model, elem);
                });
                form.elem.append(elem);
            }
        }
    }),
    //
    MultiField = lux.MultiField = ChoiceField.extend({
        //
        init: function (options) {
            this.options = Object(options);
            this.options.multiple = 'multiple';
        }
    }),
    //
    TextArea = lux.TextArea = Field.extend({
        tagName: 'textarea'
    }),
    //
    KeywordsField = lux.KeywordsField = Field.extend({

        validate: function (instance, value) {
            if (_.isString(value)) {
                var result = [];
                _(value.split(',')).forEach(function (el) {
                    el = el.trim();
                    if (el) {
                        result.push(el);
                    }
                });
                return result;
            } else if (!_.isArray(value)) {
                var val = [];
                _(value).forEach(function (v) {
                    val.push(v);
                });
                return val;
            } else {
                return value;
            }
        }
    });
    //
    // A proxy for select2
    $.fn.Select = function (options) {
        options || (options = {});
        var self = this;
        require(['select'], function () {
            if (_.isObject(options)) options.width = 'element';
            self.select2(options);
        });
        return this;
    };

    //
    // Select2 hook for lux set_value_hooks
    var get_select2_value = function (element, value) {
        if (element.hasClass('select2-offscreen')) {
            element.select2('val', value);
            return true;
        }
    };
    //
    lux.set_value_hooks.push(get_select2_value);


    var Grid = lux.Grid = lux.createView('grid', {

        initialise: function (options) {
            var self = this;
            this.elem.addClass('grid').addClass('fluid');

            if (options.rows) {
                _(options.rows).forEach(function (row) {
                    self.addRow(row);
                });
            }
        },
        //
        addRow: function (row) {
            var elem = $(document.createElement('div')).addClass(
                'row').addClass('grid24').appendTo(this.elem);
            //
            _(row).forEach(function (col) {
                var size = 'span' + col;
                elem.append($(document.createElement('div')).addClass(
                    'column').addClass(size));
            });
            return elem;
        }
    });
    //
    // Add full-screen
    var Fullscreen = lux.Fullscreen = lux.createView('fullscreen', {
        //
        defaults: {
            zindex: 2010,
            icon: 'times-circle',
            themes: ['default', 'inverse']
        },
        //
        initialise: function (options) {
            var container = $(document.createElement('div')).addClass(
                    'fullscreen').css({'z-index': options.zindex});

            this.wrap = $(document.createElement('div')).addClass(
                'fullscreen-container').appendTo(container);
            this.side = $(document.createElement('div')).addClass(
                'fullscreen-sidebar').appendTo(container);
            this.sidebar = buttonGroup({vertical: true}).appendTo(this.side);
            //
            this.themes = options.themes;
            this.theme = 1;
            this.exit = new Button({
                icon: options.icon,
                title: 'Exit full screen'
            });
            this.exit.elem.appendTo(this.sidebar);
            this.theme_button = new Button({
                icon: 'laptop',
                title: 'theme'
            });
            this.theme_button.elem.appendTo(this.sidebar);
            //
            this._wrapped = {
                elem: this.elem,
                previous: this.elem.prev(),
                parent: this.elem.parent()
            };
            //
            this.setElement(container);
            this.toggle_skin();
        },
        //
        render: function () {
            var self = this;
            if (!self.elem.parent().length) {
                //
                self.exit.elem.click(function () {
                    self.remove();
                });
                //
                self.theme_button.elem.click(function () {
                    self.toggle_skin();
                });
                self.wrap.append(this._wrapped.elem);
                self.elem.appendTo(document.body);
            }
        },
        //
        remove: function () {
            var w = this._wrapped;
            if(w.previous.length) {
                w.previous.after(w.elem);
            } else {
                w.parent.prepend(w.elem);
            }
            return this._super();
        },
        //
        toggle_skin: function () {
            var themes = this.themes,
                old_theme = this.theme;
            this.theme = old_theme ? 0 : 1;
            this.theme_button.setSkin(themes[old_theme]);
            this.setSkin(themes[this.theme]);
        }
    });

    //  Dialog
    //  -----------------------
    var Dialog = lux.Dialog = lux.createView('dialog', {
        //
        jQuery: true,
        //
        selector: '.dialog',
        //
        defaultElement: 'div',
        //
        defaults: {
            className: null,
            show: true,
            keyboard: true,
            // Can the dialog be closed
            closable: null,
            // Can the dialog be collapsable
            collapsable: false,
            // If ``collapsable`` is ``true``, this parameter controls how the
            // dialog is rendered the first time.
            collapsed: false,
            dragdrop: false,
            fullscreen: false,
            title: null,
            body: null,
            footer: null,
            modal: false,
            modal_zindex: 1040,
            autoOpen: true,
            width: null,
            height: null,
            top: null,
            skin: 'default',
            icons: {
                open: 'plus-circle',
                close: 'minus-circle',
                remove: 'times',
                fullscreen: 'arrows-alt'
            },
            buttons: {
                size: 'mini'
            }
        },
        // Create the dialog
        initialise: function (options) {
            var self = this,
                elem = this.elem.addClass('dialog').addClass(
                    options.className).hide(),
                closable = options.closable,
                title = elem.attr('title') || options.title,
                header = $(document.createElement('div')).addClass('header'),
                wrap = $(document.createElement('div')).addClass('body-wrap'),
                h3 = $(document.createElement('h3')),
                toggle;
            //
            if (!elem.attr('id')) elem.attr('id', this.cid);
            this.setSkin(options.skin);
            //
            this._body = $(document.createElement('div')).addClass(
                'body').append(elem.contents());
            this._foot = null;
            self.buttons = $(document.createElement('div')).addClass(
                'btn-group').addClass('pull-right');
            header.append(self.buttons).append(h3);
            if (title) {
                h3.append(title);
            }
            elem.empty().append(header).append(wrap.append(this._body));
            if (options.body) {
                this._body.append(options.body);
            }
            //
            this.createButton = function (opts) {
                opts = _.extend(opts || {}, options.buttons);
                if (!opts.skin) opts.skin = this.getSkin();
                return new Button(opts);
            };
            //
            // Modal option
            var width = options.width;
            if(options.modal) {
                width = this._modalCss(options);
                elem.appendTo(document.body);
                closable = closable === null ? true : closable;
                var backdrop = $(document.createElement('div'))
                                    .addClass('modal-backdrop fullscreen')
                                    .css('z-index', options.modal_zindex);
                elem.on('remove', function () {
                    backdrop.remove();
                }).on('show', function () {
                    backdrop.appendTo(document.body);
                }).on('hide', function () {
                    backdrop.detach();
                });
            }
            // set width
            if (width) elem.width(width);
            // set height
            if (options.height) this._body.height(options.height);
            if (options.collapsable) self._addCollapsable(options);
            if (closable) this._addClosable(options);
            if (options.fullscreen) this._addFullscreen(options);
            if (options.movable) this._addMovable(options);
            if (options.autoOpen) self.show();
        },
        //
        body: function () {
            return this._body;
        },
        //
        foot: function () {
            return this._foot;
        },
        //
        header: function () {
            return this.element().children('.header');
        },
        //
        title: function (value) {
            return this.header().children('h3').html(value);
        },
        //
        // make the dialog closable, unless it is already closable.
        // The optional ``options``  can specify:

        //  * ``destroy``, if true the dialog is removed when
        //    closed otherwise it is just fadeOut. Default ``True``.
        _addClosable: function (options) {
            var
            destroy = options.destroy,
            self = this,
            close = this.createButton({
                icon: options.icons.remove
            });
            close.elem.appendTo(this.buttons).click(function() {
                self.fadeOut({
                    complete: function () {
                        destroy ? self.destroy() : self.hide();
                    }
                });
            });
        },
        // Make this dialog collapsable
        _addCollapsable: function (options) {
            var self = this,
                body = this.elem.children('.body-wrap'),
                button = self.createButton(),
                hidden = false;
            // If the dialog starts life as already collapsed, avoid to show
            // the transaction by hiding the body. This requires a little trick
            // which involve removing the `collapse` class when the `hide` event
            // is triggered.
            if (options.collapsed) {
                hidden = true;
                body.hide().addClass('in').one('hide', function () {
                    body.removeClass('collapse');
                });
            }
            body.on('show', function () {
                if (hidden) {
                    hidden = false;
                    body.addClass('collapse').show();
                }
                self.elem.removeClass('collapsed');
                lux.addIcon(button.elem, {icon: options.icons.close});
            }).on('hidden', function () {
                self.element().addClass('collapsed');
                lux.addIcon(button.elem, {icon: options.icons.open});
            });
            // make sure height is auto when the dialog is not collapsed at startupSSSSS
            if (!options.collapsed) {
                body.height('auto');
            }
            button.elem.appendTo(this.buttons).mousedown(function (e) {
                e.stopPropagation();
            }).click(function () {
                body.collapse('toggle');
                return false;
            });
            require(['bootstrap'], function () {
                self.elem.children('.body-wrap').collapse();
            });
        },
        //
        // Add full screen button and action
        _addFullscreen: function (options) {
            var
            fullscreen = options.fullscreen,
            button = this.createButton({
                icon: options.icons.fullscreen,
                title: 'Full screen mode'
            });
            if (!fullscreen.render) {
                // default full screen
                fullscreen = new Fullscreen({elem: this.body()});
            }
            button.elem.prependTo(this.buttons).on('click', function () {
                fullscreen.render();
            });
        },
        //
        _addMovable: function (options) {
            //var dragdrop = this.options.dragdrop;
            //if (dragdrop) {
            //    dragdrop.add(this.element(), this.header());
            //}
        },
        //
        _modalCss: function (options) {
            var width = options.width || 500;
            rules = ['#' + this.attr('id') + '{',
                     '    margin-left: -' + width/2 + 'px,',
                     '    left: 50%,',
                     '    position: absolute,',
                     'z-index: ' + (options.modal_zindex + 10) + ',',
                     'top: ' + (options.top || '25%'),
                     '}'];
            this.addStyle(rules);
            return width;
        }
    });

    //
    // Event Loop
    // --------------------------
    //
    //  The following classes implement an abstraction on top of the
    //  javascript event loop.
    //
    var StopIteration = Exception.extend({name: 'StopIteration'});

    // The `TimeCall` is a callback added by the `EventLoop` to the
    // javascript event loop engine.
    // It can be scheduled to a time in the future or executed and the next
    // frame.
    var TimedCall = Class.extend({
        init: function (deadline, callback, args) {
            this.deadline = deadline;
            this.cancelled = false;
            this.callback = callback;
            this.args = args;
        },
        //
        cancel: function () {
            this.cancelled = true;
        },
        //
        reschedule: function (new_deadline) {
            this._deadline = new_deadline;
            this._cancelled = false;
        }
    });

    var LoopingCall = Class.extend({
        init: function (loop, callback, args, interval) {
            var self = this,
                _cancelled = false,
                handler;
            //
            this.callback = callback;
            this.args = args;
            //
            var _callback = function () {
                    try {
                        this.callback.call(this, self.args);
                    } catch (e) {
                        self.cancel();
                        return;
                    }
                    _continue();
                },
                _continue = function () {
                    if (!_cancelled) {
                        if (interval) {
                            handler.reschedule(loop.time() + interval);
                            loop.scheduled.insert(handler.deadline, handler);
                        } else {
                            loop.callbacks.append(handler);
                        }
                    }
                };

            if (interval && interval > 0) {
                interval = interval;
                handler = loop.call_later(interval, _callback);
            } else {
                interval = null;
                handler = loop.call_soon(_callback);
            }
            //
            _.extend(this, {
                get cancelled() {
                    return _cancelled;
                },
                cancel: function () {
                    _cancelled = true;
                }
            });
        }
    });

    //  The `EventLoop` is a wrapper around the Javascript event loop.
    //  Useful for combining callbacks and scheduled tasks for a given
    //  application.
    var EventLoop = lux.EventLoop = Class.extend({
        //
        init: function () {
            var _callbacks = [],
                _scheduled = new SkipList(),
                running = false,
                nextframe = window.requestAnimationFrame,
                //
                // Run at every iteration
                _run_once = function (timestamp) {
                    // handle scheduled calls
                    var time = this.time(),
                        callbacks = _callbacks.splice(0);
                    _(callbacks).forEach(function (c) {
                        if (!c.cancelled) {
                            c.callback(c.args.splice(0));
                        }
                    });
                },
                _run = function (timestamp) {
                    if (running) {
                        try {
                            _run_once(timestamp);
                        } catch (e) {
                            if (e.name === 'StopIteration') {
                                running = false;
                                return;
                            }
                        }
                        if (running) {
                            nextframe(_run);
                        }
                    }
                };

            _.extend(this, {
                get callbacks() {
                    return _callbacks;
                },
                //
                get scheduled() {
                    return _scheduled;
                },
                //
                call_soon: function (callback) {
                    var call = new TimedCall(null, callback, slice(arguments, 1));
                    _callbacks.append(call);
                    return call;
                },
                //
                call_later: function (milliseconds, callback) {
                    var args = slice.call(arguments, 2),
                        call = new TimedCall(this.time() + milliseconds, callback, args);
                    _scheduled.insert(call.deadline, call);
                    return call;
                },
                //
                call_at: function (when, callback) {
                    var args = slice.call(arguments, 2),
                        call = new TimedCall(when, callback, args);
                    _scheduled.insert(call.deadline, call);
                    return call;
                },
                //
                run: function () {
                    if (!running) {
                        running = true;
                        nextframe(_run);
                    }
                },
                //
                is_running: function () {
                    return running;
                }
            });
        },
        //
        // Schedule a `callback` to be executed at every frame of the
        // event loop.
        call_every: function (callback) {
            return new LoopingCall(this, callback, slice(arguments, 1));
        },
        //
        time: function () {
            return new Date().getTime();
        },
        //
        stop: function (callback) {
            if (this.is_running()) {
                this.call_soon(function () {
                    if (callback) {
                        try {
                            callback();
                        } catch (e) {
                            console.log(e);
                        }
                    }
                    throw new StopIteration();
                });
            } else if (callback) {
                callback();
            }
        }
    });

    // Default event loop
    lux.eventloop = new EventLoop();

    var each = lux.each;

    //  Lux Utils
    //  ------------------------
    
    // Stand alone functions used throughout the lux web libraries.
    
    lux.utils = {
        //
        detector: {
            canvas: !! window.CanvasRenderingContext2D,
            /*
            webgl: (function () {
                try {
                    return !! window.WebGLRenderingContext && !! document.createElement('canvas').getContext('experimental-webgl');
                } catch( e ) {
                    return false;
                }
            }()),
            */
            workers: !! window.Worker,
            fileapi: window.File && window.FileReader && window.FileList && window.Blob
        },
        //
        allClasses: function (elem) {
            var classes = {}, all = [];
            $(elem).each(function() {
                if (this.className) {
                    $.each(this.className.split(' '), function() {
                        var name = this;
                        if (name !== '' && classes[name] === undefined) {
                            classes[name] = name;
                            all.push(name);
                        }
                    });
                }
            });
            return all;
        },
        //
        as_tag: function(tag, elem) {
            var o = $(elem);
            if (!o.length && typeof elem === "string") {
                return $('<'+tag+'>').html(elem);
            }
            if (o.length) {
                if (!o.is(tag)) {
                    o = $('<'+tag+'>').append(o);
                }
                return o;
            }
        },
        //
        closest_color: function (el, property) {
            var val = null;
            el = $(el);
            while (el.length && val === null) {
                el = el.parent();
                val = el.css(property);
                if (val == 'inherit' || val == 'transparent') {
                    val = null;
                }
            }
            return val;
        },
        //
        // Return a valid url from an array of strings. 
        urljoin: function () {
            var normalize = function (str) {
                    return str
                        .replace(/[\/]+/g, '/')
                        .replace(/\/\?/g, '?')
                        .replace(/\/\#/g, '#')
                        .replace(/\:\//g, '://');
                },
                joined = [].slice.call(arguments, 0).join('/');
            return normalize(joined);  
        },
        //
        // Return a uman redable string describing the time ``diff``.
        prettyTime: function (diff) {
            var day_diff = Math.floor(diff / 86400);
            return day_diff === 0 && (
                        diff < 2 && "1 second ago" ||
                        diff < 60 && Math.floor( diff ) + " seconds ago" ||
                        diff < 120 && "1 minute ago" ||
                        diff < 3600 && Math.floor( diff / 60 ) + " minutes ago" ||
                        diff < 7200 && "1 hour ago" ||
                        diff < 86400 && Math.floor( diff / 3600 ) + " hours ago") ||
                    day_diff === 1 && "Yesterday" ||
                    day_diff < 7 && day_diff + " days ago" ||
                    day_diff < 31 && Math.ceil( day_diff / 7 ) + " weeks ago";
        },
        //
        asDate: function (value) {
            if (value instanceof Date) {
                return value;
            } else {
                var d = parseFloat(value);
                if (d === d) {
                    return new Date(1000*d);
                } else {
                    throw new TypeError('Could not convert ' + value + ' to a date');
                }
            }
        }
    };
var math = {},
    PI = Math.PI;
//
lux.math = math;
//
$.extend(math, {
    point2d: function (x, y) {
        return {'x': x, 'y': y};
    },
    distance2d: function (p1, p2) {
        return Math.sqrt(((p1.x - p2.x) * (p1.x - p2.x)) +
                         ((p1.y - p2.y) * (p1.y - p2.y)));
    },
    // angle (in radians) between 3 points
    //        x3,y3
    //       /
    //   x2,y2
    //       \
    //       x1,y1
    angle2d: function (x1, y1, x2, y2, x3, y3) {
        var xx1 = x1-x2,
            yy1 = y1-y2,
            xx2 = x3-x2,
            yy2 = y3-y2,
            a1 = Math.atan2(xx1, yy1),
            a2 = Math.atan2(xx2, yy2);
        return a1 - a2;
    },
    degree: function (rad) {
        return 180 * rad / PI;
    },
    radians: function (deg) {
        return PI * deg / 180;
    }
});

//
var random = Math.random,
    log = Math.log,
    NV_MAGICCONST = 4 * Math.exp(-0.5)/Math.sqrt(2.0);
//
$.extend(math, {
    //
    // Normal variates using the ratio of uniform deviates algorithm
    normalvariate: function (mu, sigma) {
        var u1, u2, z, zz; 
        while (true) {
            u1 = random();
            u2 = 1.0 - random();
            z = NV_MAGICCONST*(u1-0.5)/u2;
            zz = z*z/4.0;
            if (zz <= -log(u2)) {
                break;
            }
        }
        return mu + z*sigma;
    }
});

	return _.extend(lux, prev_lux);
});