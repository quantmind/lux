define(['lodash', 'jquery'], function (_, $) {
    "use strict";

    var root = window,
        lux = {
            //version: "<%= pkg.version %>"
        },
        slice = Array.prototype.slice;
    //
    root.lux = lux;
    //
    // Showdown extensions
    lux.showdown = {};
    //
    // Create a random s4 string
    lux.s4 = function () {
        return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    };
    //
    // Create a UUID4 string
    lux.guid = function () {
        var S4 = lux.s4;
        return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
    };
    //
    lux.isnothing = function (el) {
        return el === undefined || el === null;
    };
    //
    lux.sorted = function (obj, callback) {
        var sortable = [];
        _(obj).forEch(function (elem, name) {
            sortable.push(name);
        });
        sortable.sort();
        _(sortable).forEach(function (name) {
            callback(obj[name], name);
        });
    };
    //
    // Create a lux event handler (proxy for a jQuery event)
    lux.event = function () {
        return $.Event();
    };

    var
    //
    CID_PREFIX = 'cid',
    //
    CID_FIELD = '_cid_',
    // Custom event fired by models when their custom id change
    CID_CHANGE = 'cidchange',
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
    Type = (function (t) {

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
    Class = (function (c) {
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
    Meta = Class.extend({
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
            if (fields === Object(fields)) {
                _(fields).forEach(function (field, name) {
                    this.set_field(o, name, field, true);
                }, this);
            }
            if (!o.pk()) {
                o._id = CID_PREFIX + lux.s4();
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
                if (field === this.pkname) {
                    if (value) {
                        var cid = instance.cid();
                        instance._fields[field] = value;
                        delete instance._id;
                        if (cid !== instance.cid()) {
                            instance.trigger(CID_CHANGE, [instance, cid]);
                        }
                    } else {
                        return;
                    }
                } else {
                    instance._fields[field] = value;
                }
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
    ModelType = Type.extend({
        //
        new_class: function (Prototype, attrs) {
            var mattr = {},
                meta = Prototype._meta;
            // Make sure we inherit fields for parent models
            if (meta && meta.fields) {
                mattr.fields = _.extend({}, meta.fields);
            }
            meta = _.merge(mattr, default_meta_attributes, attrs.meta);
            delete attrs.meta;
            _(meta.fields).forEach(function (field, name) {
                if (field) field.name = name;
            });
            var cls = this._super(Prototype, attrs);
            cls._meta = cls.prototype._meta = new Meta(cls, meta);
            return cls;
        }
    }),
    //
    // Model
    // --------------------------
    //
    // The base class for a model. A model is a single, definitive source
    // of data about your data. A Model consists of ``fields`` and behaviours
    // of the data you are storing.
    Model = EventClass.extend({
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
        //
        // Custom Identifier
        //
        // Uniquely identify this model and it is **always available**.
        cid: function () {
            return this._meta.name + '-' + (this.pk() || this._id);
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
        // Sync a single model
        sync: function (store, options) {
            options = Object(options);
            var callback = options.success,
                info = this._sync_data(options),
                self = this;
            if (info) {
                info.model = this._meta.name;
                info.success = function (data) {
                    self._changed = {};
                    if (callback) callback(self);
                };
                return store.execute(info);
            } else if (callback) {
                callback(self);
            }
        },
        //
        toString: function () {
            return this.cid();
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
            options = Object(options);
            var pkvalue = this.pk();
            if (this.isDeleted() && pkvalue) {
                // DELETE THE MODEL
                options.crud = Crud.delete;
                options.item = {
                    pk: pkvalue,
                    cid: this.cid()
                };
            } else if (pkvalue && this.hasChanged()) {
                // UPDATE THE MODEL
                options.crud = Crud.update;
                options.item = {
                    fields: this.toJSON(true),
                    pk: pkvalue,
                    cid: this.cid()
                };
            } else if (!pkvalue) {
                // CREATE A NEW MODEL
                data = this.toJSON();
                if (data) {
                    options.crud = Crud.create;
                    options.item = {
                        fields: data,
                        cid: this.cid()
                    };
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
                        existing, cid;
                    //
                    options = Object(options);
                    if (!_.isArray(data)) {
                        data = [data];
                    }
                    //
                    _(data).forEach(function (o) {
                        if (!(o instanceof self.model)) {
                            o = new NewModel(o);
                        }
                        cid = o.cid();
                        existing = _map[cid];
                        if (existing) {
                            if (options.merge) {
                                existing.update(o.fields());
                                if (existing.hasChanged()) {
                                    models.push(existing);
                                }
                            }
                        } else {
                            _map[cid] = o;
                            _data.push(cid);
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
            options = Object(options);
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
            options = Object(options);
            var self = this,
                groups = {},
                callback = options.success,
                errback = options.error,
                group, item;

            this.forEach(function (model) {
                var info = model._sync_data();
                if (info) {
                    group = groups[item.crud];
                    if (!group) {
                        group = groups[item.crud] = [];
                    }
                    group.push(info.item);
                }
            });
            //
            var done = [],
                fail = [];
                fire = function () {
                    if (done.length === groups.length) {
                        if (fail.length) {
                            if (errback) {
                                errback(self, done, fail);
                            }
                        } else if (callback) {
                            callback(self);
                        }
                    }
                };

            _(groups).forEach(function (group, op) {
                self.store.execute({
                    meta: self.model._meta,
                    type: op,
                    data: group,
                    success: function (data) {
                        done.push(op);
                        try {
                            self.afterSync(op, data);
                        } finally {
                            fire();
                        }
                    },
                    error: function (exc) {
                        done.push(op);
                        fail.push(op);
                        fire();
                    }
                });
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


    lux.Type = Type;
    lux.Class = Class;
    lux.EventClass = EventClass;
    lux.Model = Model;
    lux.ModelType = ModelType;
    lux.Exception = Exception;
    lux.ModelException = ModelException;
    lux.NotImplementedError = NotImplementedError;



    // Cached regex to split keys for `delegate`.
    var
    //
    delegateEventSplitter = /^(\S+)\s*(.*)$/,
    //
    viewOptions = ['model', 'collection', 'elem', 'id', 'attributes', 'className', 'tagName', 'events'],
    //
    View = lux.View = Class.extend({
        tagName: 'div',

        init: function (options) {
            this.cid = _.uniqueId('view');
            options || (options = {});
            _.extend(this, _.pick(options, viewOptions));
            if (!this.elem) {
                this.setElement($(document.CreateElement(this.tagName)), false);
            } else {
                this.elem = $(_.result(this, 'elem'));
                this.setElement(this.elem, false);
            }
        },

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
        }
    });
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
            var idx = store.search('://');
            if (idx > -1) {
                var scheme = store.substr(0, idx),
                    Store = stores[scheme];
                if (Store) {
                    return new Store(store, options, scheme);
                }
            }
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
                options.data = item.fields;
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
            // This is an execution for a single item
            if (options.item) {
                options.data = [options.item];
            }
            //
            var obj = {
                // new message id
                mid: this.new_mid(options),
                action: options.action || lux.CrudMethod[options.crud] || options.crud,
                model: options.model,
                data: options.data
            };
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
            if (options) {
                delete this._pending_messages[mid];
                if (options.item) {
                    data = data[0];
                }
            }
            if (obj.error) {
                if (options && options.error) {
                    options.error(obj.error, this, obj);
                } else {
                    logger.error(this.toString() + ' - ' + obj.error);
                }
            } else {
                if (options && options.success) {
                    options.success(data, this, obj);
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
                var mid = lux.s4();
                while (this._pending_messages[mid]) {
                    mid = lux.s4();
                }
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
                ext = this.create_extension(name, ext);
                this.extension_list.push(ext);
                this.extensions[name] = ext;
                return ext;
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

	return lux;
});