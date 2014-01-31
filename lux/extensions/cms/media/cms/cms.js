define(['lux-web'], function () {
    "use strict";

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

    // Base class for contents
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


    var inner_dialog = "<div class='content-editor'>".concat(
            "<div class='editor'>",
            "<div class='preview'>",
            "</div>",
            "</div>",
            "</div>");

    // Edit content by opening a dialog
    var edit_content_dialog = function (self, options) {
        if (self._content_dialog) {
            return self._content_dialog;
        }
        options = options || {};
        var dialog = web.dialog({
                modal: true,
                movable: true,
                fullscreen: true,
                title: 'Edit Content'
            }),
            editor = $(document.createElement('div')).addClass('editor'),
            preview = $(document.createElement('div')).addClass('preview'),
            container = $(document.createElement('div')).append(editor).append(preview),
            //
            // Create the selct element for HTML wrappers
            wrapper_select = web.create_select(cms.wrapper_types(),
                    {placeholder: 'Select a container'}),
            //
            // create the select element for content types
            content_select = web.create_select(cms.content_types(),
                    {placeholder: 'Select a Content'}),
            top = $(document.createElement('div')).addClass('top'
                    ).append(wrapper_select).append(content_select).appendTo(editor),
            edit_form = $(document.createElement('div'));
        //
        dialog.body()
            .append(container)
            .addClass('edit-content')
            .bind('close-plugin-edit', function () {
                dialog.destroy();
            });
        //
        // Change content type
        content_select.element().change(function () {
            var name = $(this).val();
            self.content = self.content_history[name];
            if (!self.content) {
                var ContentType = cms.content_type(name);
                if (ContentType) {
                    self.content = new ContentType();
                }
            }
            if (self.content) {
                web.logger.info(self + ' changed content type to ' + self.content);
                self.content_history[self.content._meta.name] = self.content;
                self.content.edit(self, container);
            } else {
                web.logger.error('Unknown content type ' + name);
            }
        });
        //
        // Change container
        wrapper_select.element().change(function () {

        });
        //
        if (self.content) {
            self.content_history[self.content._meta.name] = self.content;
            content_select.element().val(self.content._meta.name).trigger('change');
        }
        //
        return dialog;
    };
    //
    // The Html element for editing a content block
    var edit_content_element = function (self) {
        var container = $(document.createElement('div')),
            toolbar = $(document.createElement('div'))
                        .addClass('cms-position-toolbar').appendTo(container),
            group = $(document.createElement('div'))
                        .addClass('btn-group right').appendTo(toolbar),
            button = parent.dialog.create_button({icon: 'edit', size: 'mini'})
                        .click(function () {
                            self.edit_content();
                        }).appendTo(group),
            title = $(document.createElement('span')).prependTo(toolbar);
        this.button_group = group;
        this.title = title;
        container.appendTo(self.elem.parent());
        this.elem.addClass('preview').appendTo(container);
        this._container = container;
        this.content_history = {};
    };

    //
    //  ContentView
    //  ------------------------

    //  Base ``view`` class for Lux CMS.
    //  The content view can be either in ``editing`` or ``read`` mode.
    //  When in editing mode the ``this.options.editing`` attribute is ``true``.

    var ContentView = lux.View.extend({
        type: 'page',
        childType: 'grid',
        // The constructor takes an HTML or jQuery element, an ``options`` object
        // and a ``parent`` ContentView.
        init: function (elem, options, parent) {
            this.elem = $(elem);
            this.options = options || {};
            this.parentType = parent ? parent.type : null;
            this.name = this.elem.data('context');
            this.elem.addClass('cms-' + this.type).data('cmsview', this);
            this.setup();
            if (this.options.editing) {
                this.setupEdit(parent);
                web.logger.info('Created ' + this);
            }
        },
        // Setup the view by adding specific classes to the view ``elem``.
        setup: function () {},
        // Setup the view for editing mode. Called during construction.
        setupEdit: function (parent) {},
        // The parent view of this view.
        parent: function () {
            return this.container().closest('.cms-'+this.parentType).data('cmsview');
        },
        // Fetch the child view at ``index``.
        child: function (index) {
            var child;
            this.iter(function (c, idx) {
                if (idx === index) {
                    child = c;
                    return lux.breaker;
                }
            });
            return child;
        },
        // Number of children
        numChildren: function () {
            return this.childrenElem().length;
        },
        // jQuery element containing all children
        childrenElem: function () {
            return this.elem.find('.cms-' + this.childType);
        },
        // Iterate over children views
        iter: function (callback) {
            _(this.childrenElem()).forEach(function (child, index) {
                return callback($(child).data('cmsview'), index);
            });
        },
        //
        page: function () {
            return $('.cms-page').data('cmsview');
        },
        grid: function () {
            return this.parent().grid();
        },
        current_column: function () {
            return this.page().current_column();
        },
        // position within its parent
        index: function () {
            var parent = this.parent(),
                index = -1,
                elem = this.elem[0];
            if (parent) {
                _(parent.childrenElem()).forEach(function (c, idx) {
                    if (elem === c) {
                        index = idx;
                        return lux.breaker;
                    }
                });
            }
            return index;
        },
        // The default render method
        render: function (contents) {
            contents = this.create_children(contents);
            _(contents).forEach(function (content, index) {
                var child = this.child(index);
                if (!child) {
                    this.create_child(null, content);
                } else {
                    child.render(content);
                }
            }, this);
            this.elem.fadeTo('fast', 1);
        },
        //
        // Create child.
        create_child: function (elem, content) {
            var View = ContentViewMap[this.childType];
            if (!View) {
                throw new lux.NotImplementedError(this + ' has no create_child method.');
            }
            if (!elem) elem = $(document.createElement('div'));
            var child = new View(elem, this.options, this);
            this.elem.append(child.container());
            child.render(content);
            return child;
        },
        //
        // Create children from HTML children of ``this.elem``. This operation
        // is performed once only, when no children available.
        create_children: function (content) {
            if (!this.numChildren()) {
                var self = this;
                this.elem.children().detach().each(function (index) {
                    self.create_child(this, content ? content[index]: null);
                });
                var len = this.numChildren();
                if (len && content) {
                    return content.splice(len);
                }
            }
            return content;
        },
        // The jQuery element containing this view. It can be different form the
        // view jQuery ``elem``.
        container: function () {
            if (this.dialog) {
                return this.dialog.element();
            } else {
                return this.elem;
            }
        },
        //
        // Retrieve a column from the child at ``index``. If index is not provided
        // or is out of bounds, retrieve the column from the first child
        get_column: function (index) {
            var child = this.childrenElem().first(),
                view = child.data('cmsview');
            return view.get_column();
        },
        // Layout information for this view. This method is invoked
        // when the page needs to sync with the backend database
        layout: function () {
            var all = [],
                layout;
            this.iter(function (child) {
                layout = child.layout();
                if (layout) all.push(layout);
            });
            return all.length ? all : null;
        },
        // Create a ``DragDrop`` dialog for this view. used by ``RowView``
        // and ``BlockView``.
        drag_drop_dialog: function (parent, opts) {
            var dialog = web.dialog(opts),
                page = this.page();
            // append the row element to the body of the row dialog
            dialog.body().append(this.elem);
            parent.elem.append(dialog.container().addClass(opts.dropzone));
            this.dialog = dialog;
            dialog.element().bind('removed', function () {
                page.sync();
            });
            return dialog;
        },
        //
        toString: function () {
            var n = this.index();
            return n === -1 ? this.type : this.type + '-' + n;
        }
    });

    //  PageView
    //  --------------

    //  Handle the CMS page. This is the view which contains children ``GridView``.
    //  GridView are created for all descendant which match the
    //  ``.cms-grid`` selector.
    var PageView = ContentView.extend({
        // Constructor from a model instance and a cms instance of the cms web
        // extension.
        init: function (model, cms) {
            var self = this;
            this.model = model;
            this.cms = cms;
            this._super(cms.element(), cms.options);
            _(this.childrenElem()).forEach(function (elem) {
                elem = $(elem);
                var next = elem.next(),
                    parent = elem.parent();
                var g = new GridView(elem, self.options, self);
                if (next.length) {
                    next.before(g.container());
                } else {
                    parent.append(g.container());
                }
            });
        },
        // Setup page
        //  * Add control button "Add new block"
        //  * Setup Drag & Drop for rows and blocks.
        setupEdit: function (parent) {
            var cms = this.cms,
                control = $('.cms-control');
            if (!control.length) {
                control = $(document.createElement('div'))
                    .addClass('cms-control').prependTo(document.body);
            }
            delete this.cms;
            this.control = web.dialog(control, this.options.page);
            control.show();
            cms.backend.element().prependTo(this.control.header());
            this._add_block_control();
            //
            // Create Drag & drop elements for the dialogs
            if (this.options.block.dragdrop) {
                this.options.block.dragdrop = this._create_drag_drop(this.options.block);
            }
            if (this.options.row.dragdrop) {
                this.options.row.dragdrop = this._create_drag_drop(this.options.row);
            }
        },
        //
        parent: function () {
            return null;
        },
        //
        page: function () {
            return this;
        },
        grid: function () {
            return null;
        },
        index: function () {
            return -1;
        },
        // Return the current ``ColumnView`` element.
        get_current_column: function () {
            return this._current_column;
        },
        set_current_column: function (column) {
            if (this._current_column) {
                this._current_column.elem.removeClass('active');
            }
            this._current_column = column;
            if (column) {
                web.logger.info('Selected current ' + column);
                column.elem.addClass('active');
            }
        },
        // Override layout to pick up children layouts
        layout: function () {
            var all = {},
                layout;
            this.iter(function (child) {
                layout = child.layout();
                if (layout) all[child.name] = layout;
            });
            return all;
        },
        // Render page from model content or from html if model is not provided.
        render: function () {
            if (this.model) {
                var children = {},
                    child;
                this.iter(function (child) {
                    children[child.name] = child;
                });
                _(this.model.get('content')).forEach(function (grid, name) {
                    child = children[name];
                    if (child) child.render(grid);
                }, this);
            } else {
                this.iter(function (child) {
                    child.render();
                });
            }
        },
        //
        sync: function (options) {
            this.model.set('content', this.layout());
            web.logger.info(this + ' sync with backend');
            this.model.sync(options);
        },
        //
        // Create the "Add Block" button for adding a block into a column.
        _add_block_control: function () {
            var self = this,
                options = self.options,
                control = this.control,
                button = control.create_button({
                    icon: options.add_block_icon,
                    title: 'Add new block'
                }),
                select = self.select_layouts().addClass(options.skin);
            self.control.buttons.prepend(select).prepend(button);
            button.click(function () {
                var templateName = select.val(),
                    column = self.get_current_column();
                //
                // Add the block to the current column
                if (!column || column.index() < 0) {
                    column = self.get_column();
                    self.set_current_column(column);
                }
                if (column) {
                    column.create_child(null, {template: templateName});
                } else {
                    web.logger.warning('No column available!');
                }
            });
        },
        //
        select_layouts: function () {
            var s = $(document.createElement('select'));
            BLOCK_TEMPLATES.each(function (_, name) {
                s.append($("<option></option>").attr("value",name).text(name));
            });
            return s;
        },
        //
        // Create the drag and drop for both Rows and Blocks
        _create_drag_drop: function (opts) {
            var self = this,
                dd = new web.DragDrop({
                    dropzone: '.' + opts.dropzone,
                    placeholder: $(document.createElement('div')).addClass(opts.dropzone),
                    onDrop: function (elem, e) {
                        dd.moveElement(elem, this);
                        self.sync();
                    }
                });
            dd.add('.' + opts.dropzone, '.' + opts.dropzone + ' > .header');
            return dd;
        }
    });

    //
    //  Grid View
    //  --------------------
    //
    //  View manager for a Grid, or better a CmsContext. A grid is a container
    // of Rows. In editing mode it is used to add and remove rows.
    var GridView = ContentView.extend({
        type: 'grid',
        childType: 'row',
        //
        setupEdit: function (parent) {
            var self = this,
                dialog = this.dialog = web.dialog(this.options.grid),
                add_row = dialog.create_button({
                    icon: this.options.add_row_icon,
                    title: 'Add new row'
                }),
                select = $(document.createElement('select')).addClass(dialog.options.skin);
            //
            ROW_TEMPLATES.each(function (_, name) {
                select.append($("<option></option>").attr("value", name).text(name));
            });
            dialog.buttons.prepend(select).prepend(add_row);
            // Adds a bright new row
            add_row.click(function () {
                self.create_child(null, {template: select.val()});
            });
            dialog.title(this.name);
            dialog.body().append(this.elem.fadeTo('fast', 1));
        },
        grid: function () {
            return this;
        },
        index: function () {
            return this.name;
        },
        toString: function () {
            return this.type + '-' + this.name;
        }
    });

    //  Row View
    //  -------------------
    //
    //  Rows are created with a prefixed number of children, the columns. They
    //  are rendered by the template chosen when the Row is created.
    var RowView = ContentView.extend({
        type: 'row',
        childType: 'column',
        templates: ROW_TEMPLATES,
        //
        setup: function () {
            this.elem.addClass('row grid' + this.options.columns);
            this.templateName = this.elem.data('template');
        },
        //
        setupEdit: function (parent) {
            this.drag_drop_dialog(parent, this.options.row);
        },
        //
        render: function (content) {
            this.template = this.get_template(content);
            if (content && content.children)
                content = content.children.splice(0, this.template.length);
            else content = [];
            for (var i=content.length;i<this.template.length;i++) content[i] = null;
            content = this.create_children(content);
            var start = this.template.length - content.length;
            _(content).forEach(function (c, index) {
                var child = this.child(index+start);
                if (!child) this.create_child(null, content[index]);
                else child.render(content[index]);
            }, this);
        },
        //
        create_child: function (elem, content) {
            var c = this.numChildren();
            if (c < this.template.length) {
                var child = this._super(elem, content);
                child.container().addClass('column span' + this.template[c]*this.options.columns);
                return child;
            }
        },
        //
        get_template: function (content) {
            var template = this.templateName ? this.templates.get(this.templateName) : null;
            if (content && content.template) {
                var temp = this.templates.get(content.template);
                if (temp) {
                    this.templateName = content.template;
                    template = temp;
                }
            }
            if (!template) {
                this.templateName = this.templates.order[0];
                template = this.templates.get(this.templateName);
            }
            if (this.dialog) this.dialog.title(this.templateName);
            return template;
        },
        // Keep the location of columns in a row. if no columns have data skip the row
        layout: function () {
            var all = [],
                avail = false;
            _(this.childrenElem()).forEach(function (child) {
                child = $(child).data('cmsview');
                var layout = child.layout();
                all.push(layout);
                if (layout) avail = true;
            });
            if (avail) {
                return {
                    template: this.templateName,
                    children: all
                };
            }
        }
    });

    //  Column View
    //  -------------------
    //
    //  Handle the A Column within a RowView. A column is a container of several
    //  Blocks vertically aligned.
    var ColumnView = ContentView.extend({
        type: 'column',
        childType: 'block',
        setupEdit: function () {
            var self = this;
            this.elem.click(function (e) {
                self.page().set_current_column(self);
            });
        },
        get_column: function () {
            return this;
        }
    });

    //  Block View
    //  -------------------
    //
    //  The Block View inherits from the ``RowView`` since it shares several
    //  features.
    //
    //   * The number of children is fixed by the ``template`` attribute.
    //   * The ``template`` is retrieved from the data ``template`` key.
    var BlockView = RowView.extend({
        type: 'block',
        childType: 'position',
        templates: BLOCK_TEMPLATES,
        setup: function () {
            this.elem.addClass('block');
            this.templateName = this.elem.data('template');
        },
        setupEdit: function (parent) {
            this.drag_drop_dialog(parent, this.options.block);
        },
        //
        //  Create a new child (Position) within a block. Nothing special
        //  here, but it needs to override the ``RowView`` method.
        create_child: function (elem, content) {
            var c = this.numChildren();
            if (c < this.template.length) {
                var View = ContentViewMap[this.childType];
                if (!View) {
                    throw new lux.NotImplementedError(this + ' has no create_child method.');
                }
                if (!elem) elem = $(document.createElement('div'));
                var child = new View(elem, this.options, this);
                this.template.append(child, this, c);
                child.render(content);
                return child;
            }
        },
        //
        get_column: function () {
            return this.parent();
        }
    });

    //  Position View
    //  --------------------
    //
    //  The container of contents and therefore the atom of lux CMS.
    //  The content can be either retrieved via a backend (when in editing mode)
    //  Or accessed via children elements when in read mode. Childern elements
    //  have the ``field`` entry in their html data attribute. The field contains
    //  the name of the field for which the inner html of the element provides value.
    var PositionView = ContentView.extend({
        type: 'position',
        childType: null,
        setup: function () {
            var info = this.elem.attr('id');
            this.elem.addClass('content');
            if (info) {
                info = info.split('-');
                if (info.length === 2 && lux.cms.content_type(info[0])) {
                    this.content_type = {
                        content_type: info[0],
                        id: info[1]
                    };
                }
            }
        },
        //
        // Setup the editing view by adding the edit button which trigger the
        // ``edit_content`` method when clicked.
        setupEdit: function (parent) {
            var self = this,
                container = $(document.createElement('div')),
                toolbar = $(document.createElement('div'))
                            .addClass('cms-position-toolbar').appendTo(container),
                group = $(document.createElement('div'))
                            .addClass('btn-group right').appendTo(toolbar),
                button = parent.dialog.create_button({icon: 'edit', size: 'mini'})
                            .click(function () {
                                self.edit_content();
                            }).appendTo(group),
                title = $(document.createElement('span')).prependTo(toolbar);
            this.button_group = group;
            this.title = title;
            container.appendTo(this.elem.parent());
            this.elem.addClass('preview').appendTo(container);
            this._container = container;
            this.content_history = {};
        },
        //
        container: function () {
            return this._container ? this._container : this.elem;
        },
        //
        child: function (index) {
            return null;
        },
        // This method doesn't actually create any child, instead it collects
        // field information form a child ``elem`` if it is available.
        // If the ``elem`` has a ``field`` entry in the data dictionary, its
        // content is either in the inner html or in the ``value`` field in
        // the element data. The content is added to the ``content_type.fields``
        // object at ``field``.
        create_child: function (elem, content) {
            if (this.content_type && elem) {
                elem = $(elem);
                var field = elem.data('field');
                if (!this.content_type.fields) this.content_type.fields = {};
                if (field) {
                    this.content_type.fields[field] = elem.data('value') || elem.html();
                } else {
                    this.content_type.fields.jQuery = elem;
                }
            }
        },
        //
        render: function (content) {
            this.create_children(content);
            if (this.content_type) {
                this.get_content(this.content_type);
                delete this.content_type;
            } else if (content && content.content_type) {
                this.get_content(content);
            }
        },
        // Retrieve content from backend when in editing mode, otherwise
        // set the fields obtained from subelements in the ``create_child`` method.
        get_content: function (ct) {
            var ContentType = lux.cms.content_type(ct.content_type),
                self = this;
            if (ContentType) {
                var fields = this.elem.data('fields');
                if (ct.fields || fields === 0) {
                    fields = ct.fields;
                    if (ct.id) {
                        fields = fields || {};
                        fields.id = ct.id;
                    }
                    this.set(new ContentType(fields), false);
                // If id given, needs to load the content
                } else if (ct.id) {
                    ContentType._meta.get(ct.id, {
                        success: function (data) {
                            self.set(data[0], false);
                        }
                    });
                } else {
                    web.logger.warning('Could not understand content');
                }
            }
        },
        //
        layout: function () {
            if (this.content) {
                return {
                    id: this.content.pk(),
                    content_type: this.content._meta.name
                };
            }
        },
        // Set the ``content`` for this Position View. When ``sync`` is not ``false``
        // the content is synchronised with the backend (editing mode).
        set: function (content, sync) {
            this.content = content;
            content.render(this.elem);
            // Set the toolbar title if in editing mode
            if (this.title) {
                this.title.html(content._meta.title);
            }
            if (sync !== false) {
                var self = this,
                    page = this.page();
                // save the content if it needs to be saved
                try {
                    content.sync({
                        success: function () {
                            web.logger.info(self + ' set content to ' + self.content);
                            page.sync();
                        }
                    });
                } catch (e) {
                    web.logger.error(e);
                }
            }
        },
        get_column: function () {
            return this.parent.get_column();
        },
        // Edit content by opening a dialog.
        edit_content: function () {
            return edit_content_dialog(this);
        },
        //
        _old_edit_content: function () {
            if (!this._content_dialog) {
                var dialog = web.dialog({
                        modal: true,
                        movable: true,
                        fullscreen: true,
                        title: 'Edit Content'
                    }),
                    self = this,
                    select = $(document.createElement('select')),
                    top = $(document.createElement('div'))
                                .addClass('vpadding-small').append(select),
                    container = $(document.createElement('div')),
                    cms = lux.cms;
                //
                select.append($("<option></option>"));
                _(cms.content_types()).forEach(function (ct) {
                    var meta = ct._meta;
                    select.append($("<option></option>").val(meta.name).text(meta.title));
                });
                web.select(select, {placeholder: 'Select a Content'});
                dialog.body().append(top)
                    .append(container)
                    .addClass('edit-content')
                    .bind('close-plugin-edit', function () {
                        dialog.destroy();
                    });
                select.change(function () {
                    var name = select.val();
                    self.content = self.content_history[name];
                    if (!self.content) {
                        var ContentType = cms.content_type(name);
                        if (ContentType) {
                            self.content = new ContentType();
                        }
                    }
                    if (self.content) {
                        web.logger.info(self + ' changed content type to ' + self.content);
                        self.content_history[self.content._meta.name] = self.content;
                        self.content.edit(self, container);
                    } else {
                        web.logger.error('Unknown content type ' + name);
                    }
                });
                //
                if (this.content) {
                    this.content_history[this.content._meta.name] = this.content;
                    select.val(this.content._meta.name).trigger('change');
                }
                return dialog;
            }
            return this._dialog;
        }
    });

    // Map a view type to a view class

    var ContentViewMap = {
            'page': PageView,
            'grid': GridView,
            'row': RowView,
            'column': ColumnView,
            'block': BlockView,
            'position': PositionView
        };

    // Export to ``lux.cms`` namespace

    lux.cms.ContentView = ContentView;
    lux.cms.ContentViewMap = ContentViewMap;

    //
    //  CMS Layouts
    //  -------------------------
    //
    //  The ``Layout`` is the base class from Block Layouts. Each layouts has
    //  the ``length`` attribute which defines the number of elements
    //  within the layout.
    var Layout = lux.Class.extend({
        //
        init: function (length) {
            this.length = length;
        },
        //
        append: function (pos, block, index) {
            var elem = pos.container();
            if (this.length === 1) {
                block.elem.append(elem);
            } else {
                var inner = block.inner;
                if (!block.elem.children().length) {
                    block.elem.addClass('row grid'+block.options.columns);
                }
                elem.addClass('span' + block.options.columns/this.length).appendTo(block.elem);
            }
        }
    });
    
    var Tabs = Layout.extend({
        append: function (pos, block, index) {
            var elem = pos.container();
            if (this.length === 1) {
                block.elem.append(elem);
            } else {
                var inner = block.inner,
                    href = lux.s4(),
                    title = pos.elem.attr('title'),
                    a = $(document.createElement('a')).attr('href', '#'+href).html(title);
                if (!inner) {
                    block.ul = $(document.createElement('ul')).appendTo(block.elem);
                    block.inner = inner = $(document.createElement('div')).appendTo(block.elem);
                }
                block.ul.append($(document.createElement('li')).append(a));
                block.inner.append($(document.createElement('div')).attr('id', href).append(elem));
            }
        }
    });
    
    
    ROW_TEMPLATES.set('One Column', [1]);
    ROW_TEMPLATES.set('Half-Half', [1/2, 1/2]);
    ROW_TEMPLATES.set('33-66', [1/3, 2/3]);
    ROW_TEMPLATES.set('66-33', [2/3, 1/3]);
    ROW_TEMPLATES.set('25-75', [1/4, 3/4]);
    ROW_TEMPLATES.set('75-25', [3/4, 1/4]);
    
    ROW_TEMPLATES.set('33-33-33', [1/3, 1/3, 1/3]);
    ROW_TEMPLATES.set('50-25-25', [1/2, 1/4, 1/4]);
    ROW_TEMPLATES.set('25-25-50', [1/4, 1/4, 1/2]);
    ROW_TEMPLATES.set('25-50-25', [1/4, 1/2, 1/4]);
    
    ROW_TEMPLATES.set('25-25-25-25', [1/4, 1/4, 1/4, 1/4]);
    
    
    BLOCK_TEMPLATES.set('1 element', new Layout(1));
    BLOCK_TEMPLATES.set('2 elements', new Layout(2));
    BLOCK_TEMPLATES.set('3 elements', new Layout(3));
    BLOCK_TEMPLATES.set('2 tabs', new Tabs(2));
    BLOCK_TEMPLATES.set('3 tabs', new Tabs(3));
    BLOCK_TEMPLATES.set('4 tabs', new Tabs(4));

    //
    //  Default CMS Contents
    //  --------------------------------
    //
    //  The following are the default CMS contents shipped with ``lux-cms``
    //  javascript distribution. The are created by invoking the
    //  ''lux.cms.create_content_type`` function.

    //
    //  This Content
    //  -------------------
    //
    //  The first a probably most important content type. It represents
    //  the response obtained by the backend server without them cms
    //  system in place.
    lux.cms.create_content_type('contenturl', {
        meta: {
            title: 'Site Content',
        },
        //
        render: function (container) {
            var url = this.get('content_url'),
                elem = this.get('jQuery');
            if (url === 'this') {
                url = lux.web.options.this_url;
            }
            if (elem) {
                container.append(elem);
            } else if (url) {
                container.html('&nbsp;');
                $.ajax(url, {
                    dataType: 'json',
                    success: function (data, status, xhr) {
                        if (data.html) {
                            require(data.requires || [], function () {
                                web.refresh(container.html(data.html));
                            });
                        }
                    }
                });
            } else {
                web.logger.warning('Missing underlying page url and html');
            }
        },
        //
        get_form: function () {
            var form = lux.web.form(),
                select = form.add_input('select', {name: 'content_url'});
            $(document.createElement('option')).val('this').html('this').appendTo(select);
            _(lux.web.options.content_urls).forEach(function (value) {
                $(document.createElement('option')).val(value[1]).html(value[0]).appendTo(select);
            });
            form.add_input('submit', {value: 'Done'});
            return form;
        }
    });
    //
    //  Blank Content
    //  -------------------
    //
    //  Insert a non-breaking space.
    lux.cms.create_content_type('blank', {
        model_title: 'The content served by the url',
        render: function (container) {
            container.html('&nbsp;');
        }
    });
    //
    //  Markdown
    //  -------------------
    //
    //  Insert a non-breaking space.
    lux.cms.create_content_type('markdown', {
        model_title: 'Text using markdown',
        //
        render: function (container) {
            var self = this;
            require(['showdown'], function () {
                var raw = self.get('raw') || '',
                    converter = new Showdown.converter(),
                    html = converter.makeHtml(raw);
                web.refresh(container.html(html));
            });
        },
        //
        get_form: function () {
            var form = lux.web.form(),
                text = form.add_input('textarea', {
                    name:'raw',
                    value: this.get('raw'),
                    rows: 15,
                    placeholder: 'Write markdown'
                });
            form.add_input('submit', {value: 'Done'});
            return form;
        }
    });
    //
    //  Versions
    //  -------------------
    lux.cms.create_content_type('versions', {
        model_title: 'Versions of libraries',
        render: function (container) {
            var ul = $(document.createElement('ul')).appendTo(container);
            _(web.libraries).forEach(function (lib) {
                ul.append($('<li><a href="' + lib.web + '">' + lib.name +
                            '</a> ' + lib.version + '</li>'));
            });
        }
    });

    //
    // CRUD API Extension
    // ------------------------------
    //
    // Check for an ``api`` key in the ``html`` document data attribute.
    // If available, the api key contains the ``url`` for the site API.
    // It build the ``datatable`` ``Content``.
    lux.web.extension('api', {
        selector: 'html',
        //
        decorate: function () {
            this.url = this.element().data('api');
            if (!this.url) {
                this.on_sitemap();
            } else {
                var self = this;
                $.ajax(this.url, {
                    dataType: 'json',
                    success: function (data, status, xhr) {
                        self.on_sitemap(data);
                    }
                });
            }
        },
        //
        // When the api sitemap is available, this method setup the
        // datatable content type.
        on_sitemap: function (sitemap) {
            var self = this,
                // Dictionary of models urls and fields
                models = {},
                groups = null;
            this.models = models;
            //
            lux.cms.create_content_type('datatable', {
                model_title: 'Data Grid',
                //
                render: function (container) {
                    var elem = this.get('jQuery');
                    if (!elem) {
                        elem = $(document.createElement('div')).data({
                            colHeaders: this.get('fields'),
                            ajaxUrl: this.get('url')
                        });
                    }
                    elem.appendTo(container.html(''));
                    require(['datagrid'], function () {
                        lux.web.datagrid(elem);
                    });
                },
                //
                // Once the form is submitted get the fields to store in the
                // model content
                get_form_fields: function (arr) {
                    var data = this._super(arr),
                        api_model = models[data.url];
                    if (api_model) {
                        var columns = [];
                        if (data.fields) {
                            each(data.fields, function (id) {
                                columns.push(api_model.map[id]);
                            });
                        } else {
                            columns = api_model.fields;
                        }
                        data.fields = columns;
                        return data;
                    } else {
                        return {};
                    }
                },
                //
                get_form: function () {
                    // The select model is not yet available, create it.
                    if(!groups && sitemap) {
                        groups = self.create_groups(sitemap);
                    }
                    if (groups) {
                        return self.create_form(groups);
                    }
                }
            });
        },
        //
        // sitemap is a list of api section handlers
        create_groups: function (sitemap) {
            var groups = [],
                models = this.models;
            //
            // Add options to the model select widgets
            each(sitemap, function (section) {
                var group = $(document.createElement('optgroup')).attr('label', section.name);
                groups.push(group);
                each(section.routes, function (route) {
                    $(document.createElement('option'))
                             .val(route.api_url).html(route.model).appendTo(group);
                    // Add the route to the models object
                    models[route.api_url] = route;
                });
            });
            return groups;
        },
        //
        // Create the form for adding a data grid
        create_form: function (sessions) {
            var form = lux.web.form(),
                select_model = form.add_input('select', {name: 'url'}),
                models = this.models;
            select_model.append($(document.createElement('option')).html('Choose a model'));
            each(sessions, function (group) {
                select_model.append(group);
            });
            // Create the fields multiple select
            var fields = form.add_input('select', {
                multiple: 'multiple',
                name: 'fields'
            }).select2({
                placeholder: 'Select fields to display'
            });
            form.add_input('checkbox', {
                name: 'editable',
                label: 'Editable'
            });
            form.add_input('checkbox', {
                name: 'footer',
                label: 'Display footer'
            });
            form.add_input('submit', {value: 'Done'});
            //
            // When a model change, change the selction as well.
            select_model.select2().change(function (e) {
                var url = $(this).val(),
                    model = models[url],
                    options = model.options;
                fields.val([]).trigger("change");
                fields.children().remove();
                if (options) {
                    each(options, function (option) {
                        fields.append(option);
                    });
                } else {
                    model.options = options = [];
                    model.map = {};
                    each(models[url].fields, function (field) {
                        var option = $(document.createElement('option'))
                                        .val(field.code).html(field.name);
                        model.map[field.code] = field;
                        options.push(option);
                        fields.append(option);
                    });
                }
            });
            return form;
        }
    });

    //
    //  lux web CMS extension
    //  --------------------------------
    //
    //  This is the javascript handler of ``lux.extensions.cms``.
    //  Updates to the backend are either via a websocket or ajax requests.
    lux.web.extension('cms', {
        selector: 'div.cms-page',
        //
        options: {
            editing: false,
            // backend type, choose websocket if possible
            backend_url: null,
            // icon for the button which add a new row in a grid
            add_row_icon: 'columns',
            // icon for the button which add a new block in a column
            add_block_icon: 'plus',
            //
            skin: 'control',
            //
            row_control_class: 'add-row',
            //
            columns: 24,
            //
            // Options for the dialog controlling page inputs
            page: {
                collapsable: true,
                collapsed: true,
                class_name: 'control',
                skin: 'inverse',
                buttons: {
                    size: 'default'
                }
            },
            // Options for the dialog controlling one grid
            grid: {
                collapsable: true,
                skin: null,
                class_name: 'control',
                buttons: {
                    size: 'default'
                }
            },
            // Options for the row dialog
            row: {
                closable: true,
                collapsable: true,
                skin: 'default',
                size: 'mini',
                dragdrop: false,
                dropzone: 'row-control'
            },
            // Options for the block dialog
            block: {
                closable: true,
                collapsable: true,
                skin: 'primary',
                size: 'mini',
                dragdrop: true,
                dropzone: 'block-control'
            }
        },
        //
        // The decorator called by ``lux.web``
        decorate: function () {
            var self = this,
                options = self.options,
                elem = self.element(),
                control = $('.cms-control');
            // In editing mode, set-up grids
            if (options.editing) {
                //self._handle_close();
                elem.addClass('editing');
                //
                // Create backend
                self.backend = web.backend({
                    host: options.backend_url,
                    hartbeat: 5
                });
                //
                lux.cms.set_transport(self.backend.socket);
                lux.cms.get(options.editing, {
                    success: function (page) {
                        self.view = new PageView(page[0], self);
                        self.view.render();
                    }
                });
            } else {
                self.view = new PageView(null, this);
                self.view.render();
            }
        },
        //
        _handle_close: function () {
            $(window).bind('beforeunload', function (e) {
                e.preventDefault();
                return false;
            });
        }
    });

    //  lux web grid CMS decorator
    //  -----------------------------------------
    //
    lux.web.extension('grid', {
        defaultElement: 'div',
        //
        options: {
            template: 'Half-Half',
            columns: 24
        },
        //
        decorate: function () {
            var template = ROW_TEMPLATES.get(this.options.template),
                options = this.options,
                elem = this.element();
            if (!template) {
                this.options.template = 'Half-Half';
                template = ROW_TEMPLATES.get(this.options.template);
            }
            this.template = template;
            elem.addClass('row grid'+this.options.columns);
            _(this.template).forEach(function (width) {
                var span = width*options.columns,
                    col = $(document.createElement('div')).addClass('column span'+span);
                elem.append(col);
            });
        }
    });
//
});