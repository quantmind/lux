    //
    var
    //
    views = cms.views = {},
    //
    //  ContentView
    //  ------------------------

    //  Base ``view`` class for Lux CMS.
    //  The content view can be either in ``editing`` or ``read`` mode.
    //  When in editing mode the ``this.options.editing`` attribute is ``true``.

    BaseContentView = views.base = lux.View.extend({
        // The constructor takes an HTML or jQuery element, an ``options`` object
        // and a ``parent`` ContentView.
        initialise: function (options) {
            this.parentType = options.parent ? options.parent.type : null;
            delete options.parent;
            this.options = options;
            this.store = this.options.store;
            this.name = this.elem.data('context');
            this.elem.addClass('cms-' + this.type).data('cmsview', this);
        },
        //
        // render the view and build children
        render: function () {
            var self = this;
            this.elem.children().each(function () {
                self.create_child(this);
            });
            this.elem.fadeTo('fast', 1);
        },
        // Setup the view for editing mode. Called during construction.
        setupEdit: function () {
            var self = this;
            if (this.childType && !this.editing) {
                _(this.childrenElem()).forEach(function(elem) {
                    var child = $(elem).data('cmsview');
                    if (child) {
                        child.setupEdit();
                    } else {
                        self.log('could not find editing element', 'WARNING');
                    }
                });
            }
            this.editing = true;
        },
        //
        // The parent view of this view.
        parent: function () {
            if (this.parentType) {
                return this.container().closest('.cms-'+this.parentType).data('cmsview');
            }
        },
        //
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
        //
        // jQuery element containing all children
        childrenElem: function () {
            if (this.childType) {
                return this.elem.find('.cms-' + this.childType);
            } else {
                return [];
            }
        },
        //
        // Iterate over children views
        iter: function (callback) {
            _(this.childrenElem()).forEach(function (child, index) {
                callback($(child).data('cmsview'), index);
            });
        },
        //
        page: function () {
            return this.parent().page();
        },
        //
        grid: function () {
            return this.parent().grid();
        },
        //
        current_column: function () {
            return this.page().current_column();
        },
        //
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
        //
        // Create child element and append it to this view
        create_child: function (elem, content) {
            if (this.childType) {
                var View = views[this.childType],
                    options = this.options;
                if (!View) {
                    throw new lux.NotImplementedError(this + ' has no create_child method.');
                }
                options.elem = elem;
                options.parent = this;
                var child = new View(options);
                if (content === Object(content)) {
                    child.elem.data(content);
                }
                child.render(this);
                return child;
            }
        },
        //
        // The jQuery element containing this view.
        //
        // It can be different form the view jQuery ``elem``.
        container: function () {
            return this.dialog ? this.dialog.element() : this.elem;
        },
        //
        // Retrieve a column from the child at ``index``. If index is not provided
        // or is out of bounds, retrieve the column from the first child
        get_column: function (index) {
            var child = this.childrenElem().first(),
                view = child.data('cmsview');
            return view.get_column();
        },
        //
        // Layout information for this view.
        //
        // This method is invoked when a view needs to sync with the backend
        // database. By default a view returns an array containing the layout
        // information of its children.
        layout: function () {
            var all = [],
                layout;
            this.iter(function (child) {
                layout = child.layout();
                if (layout) all.push(layout);
            });
            return all.length ? all : null;
        },
        //
        // Create dialog
        _create_edit_dialog: function (opts) {
            if (!this.dialog) {
                this.dialog = web.dialog(opts);
                this.elem.before(this.dialog.element());
                this.dialog.body().append(this.elem);
            }
            return this.dialog;
        },
        //
        log: function (msg, lvl) {
            var page = this.page();
            if (page && page.logger) {
                if (lvl) {
                    page.logger.html('<p class="text-danger">' + lvl + ': ' + msg + '</p>');
                } else {
                    page.logger.html('<p>' + msg + '</p>');
                }
            }
        },
        //
        toString: function () {
            var n = this.index();
            return n === -1 ? this.type : this.type + '-' + n;
        }
    }),

    //  PageView
    //  --------------

    //  Handle the CMS page.
    //  This is the view which contains children ``GridView``.
    //  GridView are created for all descendant which match the
    //  ``.cms-grid`` selector.
    //  A page does not add any child during editing, it is just a container
    //  of grid elements.
    PageView = views.page = BaseContentView.extend({
        type: 'page',
        //
        childType: 'grid',
        //
        // Setup the view and build children which match cms
        render: function () {
            var self = this;
            this.childrenElem().each(function () {
                self.create_child(this);
            });
            // setup editing first
            if (this.options.editing) {
                self.model = new Page({id: this.options.editing});
                this.setupEdit();
            }
        },
        //
        // Setup editing view
        setupEdit: function () {
            if (!this.editing) {
                var control = $('.cms-control');
                this.logger = $('<div class="cms-info"></div>');
                if (!control.length) {
                    control = $(document.createElement('div'))
                        .addClass('cms-control').prependTo(document.body);
                }
                this.control = web.dialog(control, this.options.page);
                this.control.header().prepend(this.logger);
                control.show();
                this._add_block_control();
                //
                // Create Drag & drop elements for the dialogs
                if (this.options.block.dragdrop) {
                    this.options.block.dragdrop = this._create_drag_drop(this.options.block);
                }
                if (this.options.row.dragdrop) {
                    this.options.row.dragdrop = this._create_drag_drop(this.options.row);
                }
                this._super();
            }
        },
        //
        page: function () {
            return this;
        },
        //
        grid: function () {
            return null;
        },
        //
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
                this.log('Selected current ' + column);
                column.elem.addClass('active');
            }
        },
        //
        // Returns an object rather than a list of children layouts
        layout: function () {
            var all = {},
                layout;
            this.iter(function (child) {
                layout = child.layout();
                if (layout) all[child.name] = layout;
            });
            return all;
        },
        //
        // Synchronise this view with the backend
        sync: function () {
            var self = this;
            this.model.set('content', this.layout());
            this.log('saving layout...');
            self.model.sync(self.store, {
                success: function () {
                    self.log('Layout saved');
                }
            });
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
                    column.add_block(templateName);
                } else {
                    self.log('WARNING: No column available!');
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
        // Enable drag and drop
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
    }),

    //
    //  Grid View
    //  --------------------
    //
    //  View manager for a Grid. A grid is a container of Rows.
    //  In editing mode it is used to add and remove Rows.
    GridView = views.grid = BaseContentView.extend({
        type: 'grid',
        //
        childType: 'row',
        //
        setupEdit: function () {
            if (!this.editing) {
                var self = this,
                    dialog = this._create_edit_dialog(this.options.grid),
                    add_row = dialog.create_button({
                        icon: this.options.add_row_icon,
                        title: 'Add new row'
                    }),
                    select = $(document.createElement('select')).addClass(dialog.options.skin);
                //
                dialog.title(this.name);
                ROW_TEMPLATES.each(function (_, name) {
                    select.append($("<option></option>").attr("value", name).text(name));
                });
                dialog.buttons.prepend(select).prepend(add_row);
                // Adds a bright new row
                add_row.click(function () {
                    var row = self.create_child(null, {template: select.val()});
                    self.elem.append(row.container());
                    row.setupEdit();
                });
                this._super();
            }
        },
        //
        grid: function () {
            return this;
        },
        //
        index: function () {
            return this.name;
        },
        //
        toString: function () {
            return this.type + '-' + this.name;
        }
    }),

    //  Row View
    //  -------------------
    //
    //  Rows are created with a prefixed number of Columns.
    //  They are rendered by the template chosen when the Row is created.
    //  Therefore no columns are added nor deleted once a Row is created.
    //
    //   * The number of children is fixed by the ``template`` attribute.
    //   * The ``template`` is retrieved from the ``data-template``.
    RowView = views.row = BaseContentView.extend({
        type: 'row',
        //
        childType: 'column',
        //
        templates: ROW_TEMPLATES,
        //
        render: function () {
            if (this.type == 'row') {
                this.elem.addClass('row grid' + this.options.columns);
            }
            this.templateName = this.elem.data('template');
            this.template = this.templateName ? this.templates.get(this.templateName) : null;
            if (!this.template) {
                this.templateName = this.templates.order[0];
                this.template = this.templates.get(this.templateName);
            }
            var self = this,
                num = this.template.length,
                index = 0;

            this.elem.children().detach().each(function () {
                if (index < num) {
                    self.template.append(self.create_child(this), self, index);
                    index += 1;
                }
            });
            // Need more children for the template
            for (; index<num; index++) {
                self.template.append(self.create_child(), self, index);
            }

        },
        //
        setupEdit: function () {
            this._create_edit_dialog(this.options[this.type]);
            this._super();
        },
        //
        // Serialise the layout of a row
        //
        // * Keep the location of columns in a row.
        // * If no columns have data skip the row
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
        },
        //
        _create_edit_dialog: function (opts) {
            if (!this.dialog) {
                var dialog = this._super(opts),
                    page = this.page();
                dialog.container().addClass(opts.dropzone);
                dialog.element().bind('removed', function () {
                    if (page) {
                        page.sync();
                    }
                });
            }
            return this.dialog;
        },
    }),

    //  Column View
    //  -------------------
    //
    //  Handle the A Column within a Row.
    //  A column is a container of several Blocks vertically aligned.
    ColumnView = views.column = BaseContentView.extend({
        type: 'column',
        //
        childType: 'block',
        //
        setupEdit: function () {
            if (!this.editing) {
                var self = this;
                this.elem.click(function () {
                    self.page().set_current_column(self);
                });
                this._super();
            }
        },
        //
        // Return self
        get_column: function () {
            return this;
        },
        //
        // Add a new block to the column
        add_block: function (templateName) {
            var child = this.create_child(null, {template: templateName});
            this.elem.append(child.container());
            this.log('Added new ' + child);
            if (this.editing) {
                child.setupEdit();
            }
        }
    });

    //  Block View
    //  -------------------
    //
    //  The Block View inherits from the ``RowView``.
    //  Blocks are displaied within a ColumnView in
    //  a vertical layout.
    var BlockView = views.block = RowView.extend({
        type: 'block',
        //
        childType: 'content',
        //
        templates: BLOCK_TEMPLATES,
        //
        get_column: function () {
            return this.parent();
        }
    }),

    //  Content View
    //  --------------------
    //
    //  The container of contents and therefore the atom of lux CMS.
    //  The content can be either retrieved via a backend (when in editing mode)
    //  Or accessed via children elements when in read mode. Childern elements
    //  have the ``field`` entry in their html data attribute. The field contains
    //  the name of the field for which the inner html of the element provides value.
    ContentView = views.content = BaseContentView.extend({
        type: 'content',
        //
        render: function () {
            var self = this,
                data = this.elem.data(),
                Content = lux.cms.content_type(data.content_type),
                content;
            if (Content) {
                // remove the content_type & cmsview
                this.wrapper = data.wrapper;
                this.skin = data.skin;
                data = _.merge({}, data);
                delete data.wrapper;
                delete data.skin;
                delete data.cmsview;
                this.elem.children().each(function () {
                    var elem = $(this),
                        field = elem.data('field');
                    if (field) {
                        data[field] = elem.html();
                    } else {
                        self.log('Field not available in content', 'WARNING');
                        //TODO: what is this?
                        //this.content_type.fields.jQuery = elem;
                    }
                });
                if (!data.keywords) data.keywords = [];
                this.set(new Content(data), false);
            }
        },
        //
        // Setup the editing view by adding the edit button which trigger the
        // ``edit_content`` method when clicked.
        setupEdit: function () {
            if (!this.editing) {
                var self = this,
                    container = $(document.createElement('div')),
                    toolbar = $(document.createElement('div'))
                                .addClass('cms-content-toolbar').appendTo(container),
                    group = $(document.createElement('div'))
                                .addClass('btn-group pull-right').appendTo(toolbar),
                    parent = this.parent(),
                    button = parent.dialog.create_button({icon: 'edit', size: 'mini'})
                                .click(function () {
                                    self.edit_content();
                                }).appendTo(group);
                this.button_group = group;
                this.title = $(document.createElement('span')).prependTo(toolbar);
                container.appendTo(this.elem.parent());
                this.elem.addClass('preview').appendTo(container);
                this._container = container;
                this.content_history = {};
                this.editing = true;
                if (this.content) {
                    this.title.html(this.content._meta.title);
                }
            }
        },
        //
        container: function () {
            return this._container ? this._container : this.elem;
        },
        //
        child: function (index) {
            return null;
        },
        //
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
                   self.log('could not understand content!', 'WARNING');
                }
            }
        },
        //
        layout: function () {
            if (this.content) {
                return {
                    content: this.content.serialize(),
                    skin: this.skin,
                    wrapper: this.wrapper
                };
            }
        },
        //
        // Set the ``content`` for this Content View.
        // When ``sync`` is not ``false``
        // the content is synchronised with the backend (editing mode).
        set: function (content, sync) {
            this.content = content;
            var wrapper = cms.wrapper_type(this.wrapper);
            this.elem.html('');
            if (wrapper) {
                wrapper.render(this);
            } else {
                content.render(this.elem, this.skin);
            }
            // Set the toolbar title if in editing mode
            if (this.title) {
                this.title.html(content._meta.title);
            }
            if (sync !== false) {
                var self = this,
                    page = this.page();
                // save the content if it needs to be saved
                content.sync(self.store, {
                    success: function () {
                        self.log(self + ' set content to ' + self.content);
                        page.sync();
                    },
                    error: function (status) {
                        self.log('ERROR while synching. ' + status);
                    }
                });
            }
        },
        //
        get_column: function () {
            return this.parent.get_column();
        },
        //
        // Edit content by opening a dialog.
        edit_content: function () {
            var root = this.page(),
                dialog = root._content_dialog;
            if (!dialog) {
                dialog = edit_content_dialog(root.options);
                root._content_dialog = dialog;
            }
            dialog.set_current_view(this);
            dialog.fadeIn();
            return dialog;
        }
    });
