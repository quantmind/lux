    //
    //  DATAGRID
    //  -------------------------
    //
    //  Requires ``lux`` and its dependencies (``jQuery`` and ``LoDash``).
    var web = lux.web,
        TH = document.createElement('th'),
        TR = document.createElement('tr'),
        TD = document.createElement('td'),
        TRH = document.createElement('tr'),
        DATAGRID = 'DATAGRID',
        DGHDROW = 'dg-hd-row',
        exports = lux,
        columnDefaults = {
            resizable: true,
            sortable: false,
            focusable: true,
            selectable: true,
            minWidth: 30
        };
    //
    TRH.className = DGHDROW;
    TR.className = 'dg-bd-row';

    var Event = lux.Class.extend({
        //
        init: function (name, scope) {
            this.name = name;
            this.scope = scope;
        },
        //
        on: function (handler) {
            this.scope.elem.bind(this.name, handler);
        },
        //
        one: function (handler) {
            this.scope.elem.one(this.name, handler);
        },
        //
        fire: function (args) {
            var e = $.Event(this.name);
            args = args || [];
            args.splice(0, 0, this.scope);
            this.scope.elem.trigger(e, args);
            return e;
        }
    });
    //  DataGridColumn
    //  ----------------
    //
    //  A column in a ``DataGrid``. It contains the ``th`` element and several
    //  important information about the column.
    var DataGridColumn = exports.DataGridColumn = lux.Class.extend({

        init: function (options) {
            var self = this;
            //
            options = _.extend({}, columnDefaults, options);
            this.th = $(TH.cloneNode(false)).data('column', this);
            if (!options.code) {
                options.code = options.name;
            }
            //
            _.extend(this, {
                //
                getOptions: function () {
                    return options;
                },
                //
                id: function () {
                    return options.id || self.index();
                },
                //
                label: function () {
                    return options.name || self.letter();
                }
            });
        },
        // Retrieve the ``DataGrid`` instance for this ``DataGridColumn``.
        datagrid: function () {
            var elem = this.th.closest('.datagrid');
            return elem.datagrid('instance');
        },
        //
        index: function () {
            return this.th.index();
        },
        //
        letter: function () {
            return lux.num_to_letter(this.th.index());
        },
        //
        render: function () {
            var name = this.name || this.letter(),
                opts = this.getOptions(),
                th = this.th;
            if (opts.minWidth) {
                th.css('min-width', opts.minWidth+'px');
            }
            this.th.html(name);
        },
        //
        // Data from input elements within this column
        inputData: function () {
        }
    });
    //  DataGrid
    //  ----------------
    //
    // A class for data in rows and columns. Simple usage:
    //
    //      $('#example').datagrid({
    //          colHeaders: ['name','surname','place of Birth'],
    //          data: [['luca','sbardella','Adria'],
    //                 ['jo','howes','Halifax']]
    //      });
    //
    // **Attributes**
    //
    // * ``elem``, The outer ``div`` jQuery element containing the table.
    // * ``columns``, list of ``DataGridColumn``
    // * ``view``, the ``DataGridView`` instance for rending the grid on a page.
    var DataGrid = exports.DataGrid = lux.Class.extend({
        //
        // DataGrid extensions
        extensions: [],
        // **AVAILABLE OPTIONS**
        //
        // default options which can be overwritten duting initialisation
        options: {
            // Auto load the grid as soon as it is ready
            autoload: true,
            // Optional model
            model: null,
            // Optional store object or url
            store: null,
            // Minimum number of rows
            minRows: 0,
            // Minimum number of columns
            minColumns: 0,
            // Maximum number of rows
            maxRows: Infinity,
            // Maximum number of columns
            maxColumns: Infinity,
            //
            // Columns can be an integer indicating the number of columns
            // or an array of column labels, objects or DataGridColumn
            columns: null,
            //
            // Can be a integer indicating the number of rows to render,
            // if provided it overrides minRows
            rows: null,
            //
            rowHeaders: false,
            // Display table footer
            foot: false,
            //
            // Callback to execute when an error during loading of data occurs
            onLoadError: null
        },
        //
        classes: {
            container: 'datagrid',
            header: 'hd',
            top: 'header',
            bottom: 'footer'
        },
        //
        // Initialise DataGrid
        init: function (elem, options) {
            var container = $(elem),
                classes = this.classes;
            this.options = options = _.merge({}, this.options, options);
            if (container.length === 0) {
                container = $(document.createElement('div'));
            } else if(elem.is('table')) {
                container = $(document.createElement('div'));
                elem.before(container);
                container.append(elem);
            }
            container.addClass(classes.container);
            // create an id if one is not available
            if (!container.attr('id')) {
                container.attr('id', 'dg-' + lux.s4());
            }
            this.elem = container;
            container.data(DATAGRID, this);
            var table = this.table();
            if(table.length === 0) {
                table = $(document.createElement('table')).appendTo(container);
            }
            table.removeClass(classes.container);
            table.prepend(this._addtag('tbody'));
            table.prepend(this._addtag('tfoot').addClass('hd'));
            if (options.foot) {
                this.show_tfoot();
            } else {
                this.hide_tfoot();
            }
            table.prepend(this._addtag('thead').addClass('hd'));
            table.prepend(this._addtag('div.' + classes.top).addClass(classes.top).hide());
            //
            // Create the data from Html if not provided
            if (!this.options.data) {
                this.options.data = _getHTML(this);
            }
            //
            // Initialise headers
            _initHeaders(this);
            if (options.rowHeaders) {
                this.show_row_headers();
            }
            if (options.foot) {
                this.show_tfoot();
            }
            //
            self.onLoadError = options.onLoadError || function(){};
            //
            if (options.rows) {
                options.minRows = Math.max(options.rows, 0);
            }
            delete options.rows;
            //
            _register_events(this);
            _add_extensions(this);
            this.setData(this.options.data);
            delete this.options.data;
            //
            if (!this.onReady.fire().isDefaultPrevented()) {
                if (options.autoload) {
                    this.load({add: true});
                }
            }
        },
        //
        //  Sets a new source for databinding and removes all rendered rows.
        //
        //  Note that this doesn't render the new rows - you can follow it with
        //  a call to render() to do that.
        setData: function (data) {
            if (!this.data) {
                if (!(data instanceof lux.Collection)) {
                    var o = this.options;
                    data = new lux.Collection(o.model, o.store);
                }
                this.data = data;
            } else {
                this.data.reset(data);
            }
            this.tbody().html('');
        },
        //
        // Load data via the datagrid store
        load: function (options) {
            var self = this,
                add = options.add;
            //
            this.data.fetch({
                data: this.inputData(),
                success: function (data) {
                    if (add) {
                        self.data.add(data);
                    } else {
                        self.setData(data);
                    }
                    self.render();
                },
                error: function (exc) {
                    self.onLoadError(exc);
                }
            });
        },
        // The Html id, always available.
        id: function () {
            return this.elem.attr('id');
        },
        // The jQuery ``table`` element
        table: function () {
            return this.elem.find('table');
        },
        // The jQuery ``thead`` element
        thead: function () {
            return this.elem.find('thead');
        },
        // The jQuery ``tbody`` element
        tbody: function () {
            return this.elem.find('tbody');
        },
        // The jQuery ``tfoot`` element
        tfoot: function () {
            return this.elem.find('tfoot');
        },
        // The ``thead tr`` jQuery element containing the table column headers.
        // The element has the ``headers`` HTML class.
        headers: function () {
            var heads = this.thead().children('tr');
            if (!heads.length) {
                heads = $(document.createElement('tr')).appendTo(this.thead());
            } else if (heads.length > 1) {
                var h = this.thead().children('tr.headers');
                heads = h.length ? h : heads.first();
            }
            return heads.addClass('headers');
        },
        // Retrieve a column of this datagrid.
        // ``elem`` can be either an HTML element or an id (string).
        column: function (elem) {
            if (typeof(elem) === 'string') {
                elem = th = this.thead().find('#' + elem);
            } else {
                elem = $(elem);
            }
            return elem.data('column');
        },
        //
        insert_column: function (col, position) {
            var tr = this.head().find('tr.headers');
            if (position === undefined && position >= tr[0].children.length) {
                this.head().append(col);
            } else {
                //
            }
        },
        //
        //
        // Gather all input data in the datagrid
        //
        // Return an object
        inputData: function () {
            var self = this,
                data = {'field': this.fields()};
            _(self.extensions).forEach(function (ext) {
                ext.inputData(self, data);
            });
            return data;
        },
        //
        //  The number of rows
        countRows: function () {
            return this.data.length;
        },
        // Retrieve the value of a cell
        getDataAtCell: function (row, col) {
            if (row >=0 && row < this.data.length) {
                return this.data[row][col];
            }
        },
        // Show row headers
        show_row_headers: function () {
            var head = this.thead(),
                th = head.find('th.row-header');
            if (!th.length) {
                var rows = head.children('tr');
                th = $(document.createElement('th')).addClass('row-header');
                if (len(rows.length) > 1) {
                    th.attr('rowspan', rows);
                }
                rows.first().append(th);
            }
        },
        // Show the table footer
        show_tfoot: function () {
            var footer = this.tfoot().children('tr');
            if (!footer.length) {
                footer = $(document.createElement('tr')).appendTo(this.tfoot());
                _(this.columns).forEach(function (col) {
                    footer.append('<td>' + col.name + '</td>');
                });
            }
            this.elem.addClass('footer');
            this.tfoot().show();
        },
        //
        hide_tfoot: function () {
            this.elem.removeClass('footer');
            this.tfoot().hide();
        },
        //
        toggle_tfoot: function () {
            if (this.elem.hasClass('footer')) {
                this.hide_tfoot();
            } else {
                this.show_tfoot();
            }
        },
        //
        _addtag: function(tag) {
            var elem = this.elem.find(tag);
            if (!elem.length) {
                tag = tag.split('.')[0];
                elem = $(document.createElement(tag));
            }
            return elem;
        },
        // A list of column codes
        fields: function () {
            var fields = [];
            _(this.columns).forEach(function (col) {
                var data = col.inputData();
                if (data) {
                    fields.push(data);
                }
            });
            return fields;
        },
        //
        // Rendering
        //
        // Render Rows in the dom
        render: function () {
            var body = this.tbody()[0],
                maxRows = this.options.maxRows,
                minRows = this.options.minRows,
                columns = this.columns,
                data = this.data;
            //
            _(this.columns).forEach(function (col) {
                col.render();
            });
            //
            if (data.length < minRows) {
                var extra = [],
                    empty = {};
                for(var i=data.length; i<minRows; i++) {
                    extra.push(empty);
                }
                data.add(extra);
            }
            //
            data.forEach(function (item, row) {
                if (row >= maxRows) return false;
                var tr = TR.cloneNode(false);
                //
                for (var j=0; j<columns.length; j++) {
                    var col = columns[j],
                        value = item[col.id()],
                        td = TD.cloneNode(false);
                    tr.appendChild(td);
                }
                //
                body.appendChild(tr);
            });
        },
        //
        toString: function () {
            return 'DataGrid - ' + this.data.toString();
        }
    });


    // Base class for Datagrid Extension classes
    var DataGridExtension = lux.Class.extend({
        inputData: function (g, data) {}
    });

    // Add a new extension to the Datagrid class
    DataGrid.Extension = function (name, attrs) {
        attrs.name = name;
        DataGrid.prototype.extensions.push(DataGridExtension.extend(attrs));
    };
