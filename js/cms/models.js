    //
    //  LUX CMS
    //  ---------------------------------

    //  Inline editing and drag & drop for blocks within a page. The layout
    //  starts with a Page which contains a given set of ``Grid`` components
    //  which are managed the ``GridView`` model.
    //
    //  Each ``Grid`` contains one or more ``Row`` components which can be added
    //  interactively. A row has several templates with a predefined set of
    //  ``Columns``.
    var ROW_TEMPLATES = new lux.Ordered(),
        BLOCK_TEMPLATES = new lux.Ordered(),
        web = lux.web,
        split_keywords = function (value) {
            if (_.isString(value)) {
                var result = [];
                _(value.split(',')).forEach(function (el) {
                    el = el.trim();
                    if (el) {
                        result.push(el);
                    }
                });
                return result;
            } else {
                return value;
            }
        };
    //
    // Content Model
    // ----------------

    // Base class for contents.
    // A new content class is created via the higher level utility function
    // ``cms.create_content_type``.
    // A content can be persistent (its data is stored in a database) or not.
    // A non-persistent content stores its data in the page layout,
    // while the persistent one has also its own database representation.
    // To mark a model persistent, add the ``persistent: true`` attribute to
    // the ``meta`` object in the class definition.
    var Content = lux.Model.extend({
        show_title: false,
        meta: {
            name: 'content',
            attributes: {
                keywords: split_keywords
            }
        },
        //
        // Retrieve content fields form an array ``arr`` of form inputs
        get_form_fields: function (arr) {
            var fields = {};
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
            return fields;
        },
        //
        // Create a jQuery Form element for customising the content.
        // Each subclass of Content can implement this method which by default
        // returns an empty form with the submit button.
        get_form: function () {},
        //
        // Render this Content into a `container`. Must be implemented
        // by subclasses
        render: function (container) {},
        //
        close: function () {
            if (this.container) {
                this.container.trigger('close-plugin-edit');
                delete this.container;
            }
        },
        //
        // Sync only if the content is persistent in the backend,
        // otherwise no need to do anything
        sync: function (options) {
            if (this._meta.persistent) {
                return this._super(options);
            } else {
                if (options && options.success) {
                    options.success.call(this._meta, this.fields());
                }
            }
        },
        //
        // Serialize the content.
        //
        // Used by the PositionView when sychronosing with backend
        serialize: function() {
            if (this._meta.persistent) {
                var pk = this.pk();
                if (pk) {
                    return pk;
                }
            } else {
                return _.extend({
                    'content_type': this._meta.name
                }, this.fields());
            }
        }
    });
    //
    // Wrapper Model
    // ----------------

    // Base class for html wrappers
    var Wrapper = lux.Class.extend({
        render: function (view) {
            view.content.render(view.elem);
        }
    });
    //
    // Page Model
    // ----------------

    // A container of ``Content`` models displaied on a grid.
    var Page = lux.Model.extend({
        meta: {
            name: 'page',
            _content_types: {},
            _wrapper_types: {},
            //
            // retrieve a content type by name
            content_type: function (name) {
                return this._content_types[name];
            },
            //
            // retrieve a wrapper type by name
            wrapper_type: function (name) {
                return this._wrapper_types[name];
            },
            //
            // Return an array of Content types sorted by name
            content_types: function () {
                return this._sorted(this._content_types);
            },
            //
            // Return an array of Wrapper types sorted by name
            wrapper_types: function () {
                return this._sorted(this._wrapper_types);
            },
            //
            // Create a new Content model and add it to the available content
            // types.
            create_content_type: function (name, attrs, BaseContent) {
                var meta = attrs.meta;
                if (!BaseContent) {
                    BaseContent = Content;
                }
                attrs.meta = attrs.meta || {};
                attrs.meta.name = name.toLowerCase();
                var ct = BaseContent.extend(attrs);
                ct._meta.set_transport(this._backend);
                this._content_types[ct.prototype._meta.name] = ct;
                return ct;
            },
            //
            // Create a new Html Wrapper model and add it to the available wrappers
            // types.
            create_wrapper: function (name, attrs, BaseWrapper) {
                if (!BaseWrapper) {
                    BaseWrapper = Wrapper;
                }
                if (!attrs.title) {
                    attrs.title = name;
                }
                attrs.name = name.toLowerCase();
                var NewWrapper = BaseWrapper.extend(attrs),
                    wrapper = new NewWrapper();
                this._wrapper_types[wrapper.name] = wrapper;
                return wrapper;
            },
            //
            set_transport: function (backend) {
                this._backend = backend;
                _(this._content_types).forEach(function (ct) {
                    ct._meta.set_transport(backend);
                });
            },
            //
            // Internal method used by `content_tyeps` and `wrapper_types`
            _sorted: function (iterable) {
                var sortable = [];
                _(iterable).forEach(function (ct) {
                    if (ct._meta) {
                        ct = ct._meta;
                    }
                    sortable.push({value: ct.name, text: ct.title});
                });
                sortable.sort(function (a, b) {
                    return a.text > b.text ? 1 : -1;
                });
                return sortable;
            }
        },
        //
        // Got new content update
        update_content: function (o) {
            var id = o.id,
                data = o.data;
            if (id && data) {
                var ContentType = this.content_type(data.content_type);
                if (ContentType) {
                    var meta = ContentType.prototype._meta;
                    return meta.update(id, data);
                }
            }
            web.logger.error('Could not understand content');
        }
    });
    //
    // CMS handler
    // -----------------------
    //
    // cms handler is given by the ``Page`` model prototype
    var cms = lux.cms = Page._meta;
    // Export ``Content`` base class
    cms.Content = Content;
    //
