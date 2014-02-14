
    var
    //
    CID = 'cid',
    // Custom event fired by models when their custom id change
    CID_CHANGE = 'cidchange',
    //
    // Test for ``_super`` methods
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
                    this.set_field(o, name, field);
                }, this);
            }
            if (!o.pk()) {
                o._id = CID + lux.s4();
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
        set_field: function (instance, field, value) {
            if (value === undefined) return;
            // Check if there is a validater for the field
            if (this.fields) {
                var f = this.fields[field];
                if (f) {
                    value = f.validate(instance, value);
                }
            }
            var prev = instance.get(field);
            if (value === prev) return;
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
                field.name = name;
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
            return fields;
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
            var pk = this.pk(),
                data;
            if (this.isDeleted() && pk) {
                // DELETE
                options.type = Crud.delete;
                options.model = {'pk': pk};
            } else if (pk && this.hasChanged()) {
                // UPDATE
                data = this.backend_data();
                delete data[this._meta.pkname];
                options.type = Crud.update;
                options.model = {
                    'data': data,
                    'pk': pk
                };
            } else if (!pk) {
                // CREATE
                data = this.backend_data();
                if (data) {
                    options.type = Crud.create;
                    options.model = {
                        'data': data,
                        cid: this.cid()
                    };
                } else {
                    return;
                }
            } else {
                return;
            }
            return store.execute(options);
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
        // Set fields data from a form
        set_form_fields: function (arr) {
            var fields = {},
                model = this;
            _(arr).forEach(function (f) {
                var values = fields[f.name];
                if (values === undefined) {
                    fields[f.name] = f.value;
                } else if($.isArray(values)) {
                    values.push(f.value);
                } else {
                    fields[f.name] = [values, f.value];
                }
            });
            // Now loop through fields in the meta class
            _(this._meta.fields).forEach(function (field) {
                var value = field.validate(model, fields[field.name]);
                if (value !== undefined) {
                    fields[field.name] = value;
                } else {
                    delete fields[field.name];
                }
            });
            //
            this._fields = fields;
            this.trigger('change', this);
        },
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
        sync: function (options) {
            options = Object(options);
            var self = this,
                groups = {},
                callback = options.success,
                errback = options.error,
                group, item;

            this.forEach(function (model) {
                var op;
                if (model.isNew()) {
                    op = Crud.create;
                    item = model.backend_fields();
                } else if(mode.isDeleted()) {
                    op = Crud.delete;
                    item = model.pk();
                } else if (mode.hasChanged()) {
                    op = Crud.update;
                    item = model.backend_fields();
                }
                if (op) {
                    group = groups[op];
                    if (!group) {
                        group = groups[op] = [];
                    }
                    group.push(item);
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
