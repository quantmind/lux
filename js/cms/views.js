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
        //
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
        // Synchronise this view with the backend
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
        //
        // Return self
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
    //   * The ``template`` is retrieved from the ``data-template``.
    var BlockView = RowView.extend({
        type: 'block',
        childType: 'position',
        templates: BLOCK_TEMPLATES,
        //
        setup: function () {
            this.elem.addClass('block');
            this.templateName = this.elem.data('template');
        },
        //
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
        //
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
                return this.content.serialize();
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

    // Map a view type to a view class

    var ContentViewMap = lux.cms.ContentViewMap = {
            'page': PageView,
            'grid': GridView,
            'row': RowView,
            'column': ColumnView,
            'block': BlockView,
            'position': PositionView
        };

    // Export to ``lux.cms`` namespace

    lux.cms.ContentView = ContentView;
