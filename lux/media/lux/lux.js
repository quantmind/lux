define(['lodash', 'jquery'], function () {
    "use strict";

    var root = window,
        lux = {
            //version: "<%= pkg.version %>"
        };
    root.lux = lux;

    var ArrayProto = Array.prototype,
        slice = ArrayProto.slice;
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
            'title': null,
            'attributes': null,
            'liveStorage': Storage,
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
                this.model = model;
                for (var name in attrs) {
                    this[name] = attrs[name];
                }
                this.title = this.title || this.name;
                this.liveStorage = new this.liveStorage(this.name+'.');
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
                if (this.attributes) {
                    var validator = this.attributes[field];
                    if (validator === undefined && field !== this.pkname) return;
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
                meta = _.extend({}, default_meta_attributes, attrs.meta || {});
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
                web.logger.level = 'debug';
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
        // Constructor
        init: function (id, html, options) {
            this._id = id;
            this._element = html;
            this.options = $.extend(true, {}, this.options, options || {});
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
            prefix = name + '-',
            lux_idkey = 'lux-' + name + '-id',
            creation_count = 0,
            makeid = function () {
                creation_count += 1;
                return prefix + creation_count;
            };
        superClass = superClass ? superClass : web.ExtInstance;
        ext.options = $.extend(true, {}, superClass.prototype.options, ext.options || {});
        ext.name = name;
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
                    options = $.extend(opts, options);
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
                    web.logger.info('Apply extension ' + name + ' to ' +
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

    //
    var CrudMethod = lux.CrudMethod = {
            create: 'POST',
            read: 'GET',
            update: 'PUT',
            destroy: 'DELETE'
        };
    //
    // Base class for backends to use when synchronising Models
    //
    // Usage::
    //
    //      backend = lux.Socket('ws://...')
    lux.Backend = lux.EventClass.extend({
        //
        options: {
            submit: {
                dataType: 'json'
            }
        },
        //
        init: function (url, options, type) {
            this.type = type;
            this.url = url;
            this.options = _.merge({}, this.options, options);
            this.submit = this.options.submit || {};
        },
        //
        // The synchoronisation method for models
        // Submit a bunch of data related to an instance of a model or a
        // group of model instances
        send: function (options) {},
        //
        submit_options: function (options) {
            if (options !== Object(options)) {
                throw new TypeError('Send method requires an object as input');
            }
            return _.extend({}, this.submit, options);
        },
        //
        toString: function () {
            return this.type + ' ' + this.url;
        }
    });
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
    /**
     * A logger class. Usage:
     * 
     * logger = new Logger();
     */
    lux.utils.Logger = function (level) {
        var handlers = [],
            logger = this,
            log_mapping = {'debug': 10, 'info': 20, 'warning': 30, 'error': 40};
        logger.level = level && log_mapping[level] ? level : 'info';
        //
        function default_formatter(msg, level) {
            return level + ': ' + msg;
        }
        function dummy_log(msg, level) {}
        //
        function log_all(level, msg) {
            for (var i=0; i<handlers.length; ++i) {
                handlers[i].log(msg, level);
            }
        }
        //
        function create_handler(options) {
            options = options || {};
            var slevel = options.level,
                formatter = options.formatter || default_formatter,
                logfunc = options.log || dummy_log,
                nlevel = function () {
                    return log_mapping[slevel ? slevel : logger.level];
                },
                format_message = function (msg, level) {
                    var nl;
                    level = level ? level : 'info';
                    level = level.toLowerCase();
                    nl = log_mapping[level];
                    if (nl !== undefined && nl >= nlevel()) {
                        return {
                            'msg': formatter(msg, level),
                            'level': level
                        };
                    }
                };
            
            if (slevel) {
                slevel = slevel.toLowerCase();
                if (!log_mapping[slevel]) slevel = null;
            }
            
            return {
                level: function () {
                    return slevel ? slevel : logger.level;
                },
                format: format_message,
                log: function(msg, level) {
                    var data = format_message(msg, level);
                    if (data) {
                        logfunc(data);
                    }
                }
            };
        }
        //
        $.each(log_mapping, function(level) {
            logger[level] = function (msg) {
                log_all(level, msg);
            };
        });
        //
        return $.extend(logger, {
            'handlers': handlers,
            addHandler: function(hnd) {
                if(hnd !== undefined && hnd.log !== undefined) {
                    handlers.push(hnd);
                }
            },
            log: function (msg, level) {
                log_all(level, msg);
            },
            addConsole: function(options) {
                if(console !== undefined && console.log !== undefined) {
                    options = options || {};
                    options.log = function(data) {
                        console.log(data.msg);
                    };
                    var console_logger = create_handler(options);
                    logger.addHandler(console_logger);
                    return console_logger;
                }
            },
            addElement: function(html_elem, options) {
                html_elem = $(html_elem);
                if (html_elem.length) {
                    html_elem.addClass('lux-logger');
                    options = $.extend({
                        log: function(data) {
                            var msg = '<pre class="' + data.level + '">' + data.msg + '</pre>';
                            html_elem.prepend(msg);
                        }
                    }, options);
                    var hnd = create_handler(options);
                    hnd.htmlElement = html_elem;
                    logger.addHandler(hnd);
                    return hnd;
                }
            }
        });
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
//
});