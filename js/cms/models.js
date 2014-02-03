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
        web = lux.web;
    //
    // Content Model
    // ----------------

    // Base class for contents.
    // A new content class is created via the higher level utility function
    // ``cms.create_content_type``.
    var Content = lux.Model.extend({
        show_title: false,
        meta: {
            name: 'content'
        },
        //
        //  Return the jQuery element for editing the content (the editor),
        //  ``position`` is an instance of ``PositionView``. This method call
        //  the ``get_form`` method.
        edit_element: function (position) {
            var self = this,
                form = this.get_form();
            if (form) {
                form.ajax({
                    beforeSubmit: function (arr) {
                        var fields = self.get_form_fields(arr);
                        self.update(fields);
                        position.set(self);
                        self.close();
                        return false;
                    }
                });
                return form.element();
            }
        },
        //
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
        get_form: function () {
            var form = lux.web.form();
            form.add_input('submit', {value: 'Done'});
            return form;
        },
        //
        // Render this Content into a `container`. Must be implemented
        // by subclasses
        render: function (container) {},
        //
        // Edit the Content at `position` in `container`.
        // `initial` is the optional initial data
        edit: function (position, container) {
            this.container = container.html('');
            if (this.show_title) {
                container.append($(document.createElement('h3')).html(this._meta.title));
            }
            var edit = this.edit_element(position);
            if (edit) {
                this.container.append(edit);
            }
        },
        //
        close: function () {
            if (this.container) {
                this.container.trigger('close-plugin-edit');
                delete this.container;
            }
        }
    });
    //
    // Wrapper Model
    // ----------------

    // Base class for html wrappers
    var Wrapper = lux.Model.extend({
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
            // Internal method used by `content_tyeps` and `wrapper_types`
            _sorted: function (iterable) {
                var sortable = [];
                _(iterable).forEach(function (ct) {
                    sortable.push({value: ct._meta.name, text: ct._meta.title});
                });
                sortable.sort(function (a, b) {
                    return a.text > b.text ? 1 : -1;
                });
                return sortable;
            },
            //
            // Create a new Content model and add it to the available content
            // types.
            create_content_type: function (name, attrs, BaseContent) {
                var meta = attrs.meta;
                if (!meta) {
                    attrs.meta = meta = {};
                }
                meta.name = name.toLowerCase();
                if (!BaseContent) {
                    BaseContent = Content;
                }
                var ct = BaseContent.extend(attrs);
                ct._meta.set_transport(this._backend);
                this._content_types[ct.prototype._meta.name] = ct;
                return ct;
            },
            //
            // Create a new Html Wrapper model and add it to the available wrappers
            // types.
            create_wrapper: function (name, attrs, BaseWrapper) {
                var meta = attrs.meta;
                if (!meta) {
                    attrs.meta = meta = {};
                }
                meta.name = name.toLowerCase();
                if (!BaseWrapper) {
                    BaseWrapper = Wrapper;
                }
                var wrapper = BaseWrapper.extend(attrs);
                this._wrapper_types[wrapper.prototype._meta.name] = wrapper;
                return wrapper;
            },
            //
            set_transport: function (backend) {
                this._backend = backend;
                _(this._content_types).forEach(function (ct) {
                    ct._meta.set_transport(backend);
                });
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
