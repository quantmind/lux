    //
    // Create a method for a derived Class
    var fnTest = /xyz/.test(function(){var xyz;}) ? /\b_super\b/ : /.*/;
    var create_method = function (type, name, attr, _super) {
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
    };
    //
    // A Type is a factory of Classes. This is the correspondent of
    // python metaclasses.
    var Type = (function (t) {

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
    }(function(){}));
    //
    // Lux base class.
    // The `extend` method is the most important function of this object.
    var Class = (function (c) {
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
    // Class With Events
    // requires jQuery loaded
    var EventClass = Class.extend({
        //
        // Bind this class to a jQuery element
        bindToElement: function (jElem) {
            this._jquery_element = jElem;
        },
        //
        trigger: function (name) {
            this.jElem().trigger(name, this, slice.call(arguments, 1));
        },
        //
        on: function (name, callback) {
            this.jElem().on(name, callback, slice.call(arguments, 2));
        },
        //
        jElem: function () {
            return this._jquery_element ? this._jquery_element : $(window);
        }
    });
    //
    // Models
    //
    var Storage = Class.extend({
            data: {},
            init: function (prefix) {
                this.prefix = prefix;
            },
            decode: function (value) {
                return value;
            },
            encode: function (value) {
                return value;
            },
            setItem: function (key, value) {
                this.data[this.prefix+key] = this.encode(value);
            },
            getItem: function (key) {
                return this.decode(this.data[this.prefix+key]);
            },
            removeItem: function (key) {
                delete this.data[this.prefix+key];
            },
            keys: function () {
                var all = [],
                    prefix = this.prefix,
                    N = this.prefix.length;
                for (var name in this.data) {
                    if (name.substring(0,N) === prefix) {
                        all.push(name.substring(N));
                    }
                }
                return all;
            },
            all: function () {
                var self = this,
                    all = [];
                _(this.keys()).forEach(function (key) {
                    all.push(self.getItem(key));
                });
                return all;
            },
            clear: function () {
                var self = this;
                _(this.keys()).forEach(function (key) {
                    self.removeItem(key);
                });
            }
        }),
        Exception = Class.extend({
            name: 'Exception',
            init: function (message) {
                this.message = message || '';
            },
            toString: function () {
                return this.name + ': ' + this.message;
            }
        }),
        ModelException = Exception.extend({name: 'ModelException'}),
        //
        NotImplementedError = Exception.extend({name: 'NotImplementedError'}),
        //
        // Default values for ``Meta`` attributes.
        default_meta_attributes = {
            'pkname': 'id',
            'name': 'model',
            'LiveStorage': Storage,
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
            // prefix for id of model instances not yet persistent
            _newprefix: 'new-',
            //
            // Initialisation, set the ``model`` attribute and the attributes
            // for this Meta. The available attributes are the same as
            // ``default_meta_attributes`` object above.
            init: function (model, attrs) {
                var LiveStorage = attrs.LiveStorage;
                delete attrs.LiveStorage;
                this.model = model;
                _.extend(this, attrs);
                this.title = this.title || this.name;
                this.liveStorage = new LiveStorage(this.name+'.');
                this._backend = null;
            },
            //
            // Initialise an instance
            init_instance: function (o, fields) {
                o._fields = {};
                o._changed = {};
                if (fields === Object(fields)) {
                    _(fields).forEach(function (field, name) {
                        this.set_field(o, name, field);
                    }, this);
                }
                if (o.pk() === undefined) {
                    var avail = true;
                    while (avail) {
                        o._id = this._newprefix + lux.s4();
                        avail = this.liveStorage.getItem(o.id());
                    }
                }
                this.liveStorage.setItem(o.id(), o);
            },
            //
            // Retrieve a ``live`` instance from the live storage. A live
            // instance is an instance of a model available in the current
            // Html doc.
            live: function (id) {
                if (id) {
                    return this.liveStorage.getItem(id);
                } else {
                    return this.liveStorage.all();
                }
            },
            //
            clear: function (id) {
                this.liveStorage.clear();
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
            set_field: function (instance, field, value) {
                if (value === undefined) return;
                // Check if there is a validater for the field
                if (this.attributes) {
                    var validator = this.attributes[field];
                    //if (validator === undefined && field !== this.pkname) return;
                    if (validator) {
                        value = validator.call(instance, value);
                    }
                }
                var prev = instance.get(field);
                if (value === prev) return;
                if (field === this.pkname) {
                    if (value) {
                        this.liveStorage.removeItem(instance.id());
                        instance._fields[field] = value;
                        delete instance._id;
                        this.liveStorage.setItem(instance.id(), instance);
                    } else {
                        return;
                    }
                } else {
                    instance._fields[field] = value;
                }
                return prev === undefined ? null : prev;
            },
            //
            // Synchronise the ``models`` with a backend server.
            sync: function (options, models) {
                var meta = this;
                if (meta instanceof Model) {
                    meta = this._meta;
                    models = [this];
                } else if (!models) {
                    models = this.liveStorage.all();
                }
                if (meta._backend) {
                    options = options || {};
                    var crud = {};
                    _(models).forEach(function (m) {
                        if (m._meta !== meta) {
                            throw new TypeError('Got an invalid model ' + m + ' in sync');
                        }
                        if (m.isNew()) {
                            meta._add_to_crud(crud, 'create', m.backend_data(), options);
                        } else if (m.isDeleted()) {
                            meta._add_to_crud(crud, 'destroy', m.pk(), options);
                        } else if (m.hasChanged()) {
                            meta._add_to_crud(crud, 'update', m.backend_data(), options);
                        } else {
                            meta._add_to_crud(crud, 'read', m.pk(), options);
                        }
                    });
                    _(crud).forEach(function (m) {
                        meta._backend.send(m);
                    });
                } else {
                    throw new ModelException('Cannot sync ' + meta + '. No backend registered.');
                }
            },
            //
            // Register the meta with a backend transport
            set_transport: function (backend) {
                this._backend = backend;
            },
            //
            toString: function () {
                return this.name;
            },
            //
            _add_to_crud: function (crud, type, data, options) {
                var opts = crud[type];
                if (!opts) {
                    opts = _.extend({}, options);
                    var success = opts.success,
                        meta = this;
                    opts.type = type;
                    opts.data = [];
                    opts.model = meta.name;
                    opts.success = function (data) {
                        data = meta.update(data);
                        if (success) {
                            success.call(this, data, slice.call(arguments, 1));
                        }
                    };
                    crud[type] = opts;
                }
                opts.data.push(data);
            }
        });
    //
    // Metaclass for models
    var ModelType = Type.extend({
        new_class: function (Prototype, attrs) {
            var mattr = {},
                meta = Prototype._meta;
            if (meta && meta.attributes) {
                mattr.attributes = meta.attributes;
            }
            meta = _.merge(mattr, default_meta_attributes, attrs.meta);
            delete attrs.meta;
            var cls = this._super(Prototype, attrs);
            cls._meta = cls.prototype._meta = new Meta(cls, meta);
            return cls;
        }
    });
    //
    // Model
    // --------------------------
    //
    // The base class for a model. A model is a single, definitive source
    // of data about your data. A Model consists of ``fields`` and behaviours
    // of the data you are storing.
    var Model = EventClass.extend({
        // Use a different metaclass
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
        // The ``id`` is always available. If the ``pk`` is not available, a temporary
        // unique identifier is used.
        id: function () {
            return this.pk() || this._id;
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
        // Data for back-end database
        // Override if needs a different implementation
        backend_data: function () {
            var fields = {};
            _(this._fields).forEach(function (value, name) {
                if (value instanceof Date) {
                    fields[name] = 0.001*value.getTime();
                } else {
                    fields[name] = value;
                }
            });
            return {id: this.id(), 'fields': fields};
        },
        //
        // Set a field value
        set: function (field, value) {
            var prev = this._meta.set_field(this, field, value);
            if (prev !== undefined) {
                this._changed[field] = prev;
                this.trigger('change', this, field);
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
        sync: function (options) {
            return this._meta.sync.call(this, options);
        },
        //
        destroy: function (options) {
            this._deleted = true;
            if (this.isNew()) {
                this._meta.liveStorage.removeItem(this.id());
                if (options && options.success) {
                    options.success(this);
                }
            } else if (!(options && options.wait)) {
                this.sync(options);
            }
        },
        //
        toString: function () {
            return this._meta.name + '.' + this.id();
        },
        //
        // Get a jQuery form element for this model.
        get_form: function () {}
    });

    lux.View = Class.extend({
        remove: function() {
            this.elem.remove();
            return this;
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
