define(['lux-web'], function () {
    "use strict";

    var Collection = lux.Collection = lux.Class.extend({

        init: function (options) {
            _new_collection(this, Object(options));
        }
    });


    var _new_collection = function (self, options) {
        var _data = [],
            Model = options.Model || lux.Model.extend({});


        _.extend(self, {
            set_items: function (data) {
                if (_.isArray(data)) {
                    _data = data;
                } else {
                    throw new lux.Exception('Collection.setItems accepts an array of objects only!');
                }
            },
            //
            get_item: function (index) {
                return _data[index];
            },
            //
            get_items: function () {
                return _data;
            },
            //
            length: function () {
                return _data.length;
            }
        });
    };

    var web = lux.web,
        TH = document.createElement('th'),
        TR = document.createElement('tr'),
        TD = document.createElement('td'),
        TRH = document.createElement('tr'),
        DATAGRID = 'DATAGRID',
        DGHDROW = 'dg-hd-row',
        exports = lux;
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
        //
        defaults: {
            resizable: true,
            sortable: false,
            minWidth: 30,
            focusable: true,
            selectable: true
        },

        init: function (options) {
            var defaults = this.defaults;
            delete this.defaults;
            _.extend(this, defaults, options);
            this.th = $(TH.cloneNode(false)).data('column', this);
            if (!this.code) {
                this.code = this.name;
            }
        },
        //
        id: function () {
            return this.th.attr('id');
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
            var name = this.name || this.letter();
            this.th.html(name);
        },
        //
        // Data from input elements within this column
        input_data: function () {
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
            // Minimum number of rows
            minRows: 0,
            // Minimum number of columns
            minColumns: 0,
            // Maximum number of rows
            maxRows: Infinity,
            // Maximum number of columns
            maxColumns: Infinity,
            //
            columns: null,
            //
            rowHeaders: false,
            // Display table footer
            foot: false
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
            // Create the data collection
            var data;
            if (!this.options.data) {
                data = _getHTML(this);
            } else {
                data = this.options.data;
            }
            delete this.options.data;
            //
            // Initialise headers
            _initHeaders(this);
            if (options.rowHeaders) {
                this.show_row_headers();
            }
            if (options.foot) {
                this.show_tfoot();
            }
            _register_events(this);
            _add_extensions(this);
            if (!this.onReady.fire().isDefaultPrevented()) {
                this.set_data(data);
                this.render();
            }
        },
        //
        //  Sets a new source for databinding and removes all rendered rows.
        //
        //  Note that this doesn't render the new rows - you can follow it with
        //  a call to render() to do that.
        set_data: function (data) {
            if (!(data instanceof Collection)) {
                data = new Collection(data);
            }
            this.data = data;
            this.tbody().html('');
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
        input_data: function () {
            var self = this,
                data = {'field': this.fields()};
            _(self.extensions).forEach(function (ext) {
                ext.input_data(self, data);
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
                var data = col.input_data();
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
                columns = this.columns,
                data = this.data;
            //
            if (!data) return;
            //
            _(this.columns).forEach(function (col) {
                col.render();
            });
            //
            for (var index=0; index<data.length(); index++) {
                var item = data.get_item(index),
                    tr = TR.cloneNode(false);

                for (var j=0; j<columns.length; j++) {
                    var col = columns[j],
                        value = item[col.code()],
                        td = TD.cloneNode(false);
                    tr.appendChild(td);
                }

                body.appendChild(tr);
            }
        }
    });


    // Base class for Datagrid Extension classes
    var DataGridExtension = lux.Class.extend({
        input_data: function (g, data) {}
    });

    // Add a new extension to the Datagrid class
    DataGrid.Extension = function (name, attrs) {
        attrs.name = name;
        DataGrid.prototype.extensions.push(DataGridExtension.extend(attrs));
    };

    //
    // Perform client side column sorting
    DataGrid.Extension('sorting', {
        //
        options: {
            sortable: false,
            sorting_icon: 'sort',
            sorting_asc_icon: 'sort-down',
            sorting_desc_icon: 'sort-up'
        },
        //
        classes: {
            enabled: 'sortable',
            sorted: 'sorted'
        },
        //
        sort_string: {
            asc: function (a, b) {
                a = (a + '').toLowerCase();
                b = (b + '').toLowerCase();
                return ((a < b) ? -1 : ((a > b) ? 1 : 0));
            },
            desc: function (a, b) {
                a = (a + '').toLowerCase();
                b = (b + '').toLowerCase();
                return ((a < b) ? 1 : ((a > b) ? -1 : 0));
            }
        },
        //
        sort_number: {
            is: function (a) {
                if(typeof(a) !== 'number') {
                    return !isNaN(a*1);
                } else {
                    return true;
                }
            },
            asc: function (a, b) {
                a = (a==="-" || a==="") ? 0 : a*1;
                b = (b==="-" || b==="") ? 0 : b*1;
                return a - b;
            },
            desc:  function (a, b) {
                a = (a==="-" || a==="") ? 0 : a*1;
                b = (b==="-" || b==="") ? 0 : b*1;
                return b - a;
            }
        },
        //
        init: function (g) {
            if (g.options.sortable) {
                var self = this;
                //
                // Inject sort method
                g.sort = function (col, acending) {
                    self.sort(g, col, acending);
                };
                //
                self._enable_sorting(g);
                //
                g.elem.on('click', 'th', function(e) {
                    var col = g.column(e.currentTarget);
                    if(col && col.sorting !== false) {
                        self.sort(g, col);
                    }
                });
            }
        },
        // Client side sorting
        sort: function (g, col) {
            var self = this,
                type = col.data_type,
                index = col.index(),
                classes = this.classes,
                rows = [],
                sorter,
                gtype,
                gtype2,
                val;
            if (g.options.rowHeaders) {
                index--;
            }
            //
            if (g.sortColumn === col) {
                g.sortOrder = g.sortOrder === 'asc' ? 'desc': 'asc';
            }
            else {
              g.sortColumn = col;
              g.sortOrder = col.direction ? col.direction : 'asc';
            }
            for (var i=0; i < g.countRows(); i++) {
                val = g.getDataAtCell(i, index);
                rows.push([i, val]);
                if (!type) {
                    gtype2 = self._guessType(val);
                    if (gtype2 === 'string') {
                        type = 'string';
                    } else if (gtype === undefined) {
                        gtype = gtype2;
                    } else if (gtype !== gtype2) {
                        type = 'string';
                    }
                }
            }
            if (!type) {
                type = gtype;
            }
            col.data_type = type;
            if (type) {
                // pick up sorter
                sorter = this['sort_' + type][g.sortOrder];
                rows.sort(function (a, b) {
                    return sorter(a[1], b[1]);
                });
                var data = [];
                _(rows).forEach(function (value) {
                    data.push(g.data[value[0]]);
                });
                g.data = data;
                _(g.columns).forEach(function (c) {
                    self.set_icon(c, g.options.sorting_icon);
                });
                this.set_icon(col, g.options['sorting_' + g.sortOrder + '_icon']);
                g.render();
            }
        },
        // Enable Sorting
        _enable_sorting: function (g) {
            var classes = this.classes,
                thead = g.thead(),
                self = this;
            _(g.columns).forEach(function (col) {
                if (col.sortable === false) {
                    col.th.removeClass(classes.enabled);
                } else {
                    self.set_icon(col, g.options.sorting_icon);
                    col.th.addClass(classes.enabled);
                }
            });
        },
        // guess type
        _guessType: function (value) {
            if (this.sort_number.is(value)) {
                return 'number';
            } else {
                return 'string';
            }
        },
        //
        set_icon: function (col, icon) {
            if (icon) {
                var a = col.th.find('a.sortable-toggle');
                if (!a.length) {
                    a = $(document.createElement('a')).addClass('sortable-toggle').appendTo(col.th);
                }
                a.html('<i class="icon-' + icon + '"></i>');
            }
        }
    });
    //  Server side data
    //  -----------------------
    //
    //  Retrieve data via AJAX or WebSockets
    DataGrid.Extension('server', {
        options: {
            ajaxUrl: null,
            ajaxDataType: 'json',
            ajaxMethod: 'GET',
            //
            websocket: null,
            // When true, the data is requested immidiately
            autoload: true
        },
        //
        init: function (g) {
            var o = g.options,
                self = this;
            if (o.ajaxUrl || o.websocket) {
                //
                g.load = function () {
                    self.load(g);
                };
                //
                // Override sort method
                g.sort = function (col, ascending) {
                    self.sort(g, col, ascending);
                };
                //
                //
                if (o.autoload) {
                    // Hook into onReady
                    g.onReady.one(function (e) {
                        e.preventDefault();
                        self.load(g);
                    });
                }
            }
        },
        // Load Data via AJAX
        load: function (g) {
            var self = this,
                o = g.options;
            $.ajax(o.ajaxUrl, {
                dataType: o.ajaxDataType,
                data: g.input_data(),
                type: o.ajaxMethod,
                success: function (data) {
                    g.data = data;
                    g.render();
                }
            });
        },
        //
        // Server side sorting
        sort: function (g, col, acending) {

        }
    });

    var CheckboxColumn = DataGridColumn.extend({

    });

    // Add a checkbox column as the first column in the datagrid
    DataGrid.Extension('checkboxSelector', {
        options: {
            checkbox_selector: false
        },

        init: function (g) {
            if (g.options.checkbox_selector && g.options.colHeaders) {
                g.options.colHeaders.splice(0, 0, new CheckboxColumn());
            }
        }
    });


    // Add a checkbox column as the first column in the datagrid
    DataGrid.Extension('RowActions', {
        //
        options: {
            row_actions: []
        },
        //
        init: function (g) {
            var o = g.options;
            if (o.colHeaders && o.row_actions && o.row_actions.length) {
                if (!o.checkbox_selector) {
                    o.checkbox_selector = true;
                    o.colHeaders.splice(0, 0, new CheckboxColumn());
                }
            }
        }
    });
    // Perform client side column sorting
    DataGrid.Extension('skin', {
        options: {
            styles: {
                'plain': '',
                'table': 'table',
                'grid': 'table-grid'
            },
            style: 'table',
            skin: 'default'
        },
        init: function (g) {
            var self = this;
            g.skin = function (name) {
                self.skin(g, name);
            };
            g.style = function (name) {
                self.style(g, name);
            };
            g.skin(g.options.skin);
            g.style(g.options.style);
        },
        skin: function (g, name) {
            var web = lux.web;
            if (web) {
                var skin = web.get_skin(g.elem);
                if (skin !== name) {
                    g.elem.removeClass(skin).addClass(name);
                }
            }
        },
        // Set the style of the table
        style: function (g, name) {
            if (g.options.styles[name] !== undefined) {
                _(g.options.styles).forEach(function (cn) {
                    g.elem.removeClass(cn);
                });
                g.elem.addClass(g.options.styles[name]);
            }
        }
    });
    //  Datagrid Responsive
    //  -----------------------
    //
    //  Tables that work responsively on small devices. To enable it set
    //  the ``responsive`` options value to ``true``.
    DataGrid.Extension('responsive', {
        init: function (g) {
            if (g.options.responsive) {
                var self = this;
                this.switched = false;
                this._render = g.render;
                g.render = function () {
                    self.render(g);
                };
                $(window).on("resize", function () {
                    self.render(g);
                });
            }
        },
        //
        render: function (g) {
            var width = $(window).width();
            if (width < 767 && !this.switched) {
                this.switched = true;
                var body = g.tbody();
                _(g.columns).forEach(function (col, index) {
                    index += 1;
                    body.find('td:nth-of-type('+index+')').attr(
                                'data-content', col.name);
                });
            } else if (width >= 767 && this.switched) {
                this.switched = false;
                this._render.call(g);
            }
        }
    });
    // jQuery extension
    $.fn.datagrid = function (options) {
        var $this = this.first(), // Use only first element from list
            instance = $this.data(DATAGRID);
        if (options === 'instance') {
            return instance;
        } else {
            if (!instance) {
                instance = new lux.DataGrid($this, options);
            }
            return instance.elem;
        }
    };

    //
    web.extension('datagrid', {
        //
        selector: '.datagrid',
        //
        defaultElement: 'div',
        //
        // table constructor
        decorate: function () {
            var elem = $(this.element()).datagrid(this.options);
            this.datagrid = elem.data(DATAGRID);
        }
    });
    //
    // Internal methods
    // ---------------------------------------------
    //
    // Internal functions used by DataGrid
    //
    //
    // Initialise table data from HTML
    var

    _getHTML = function (self) {
        var heads = self.thead().children('tr'),
            data = [];
        if (heads.length) {
            var h = this.thead().children('tr.headers');
            heads = h.length ? h : heads.last();
            heads.children('th').each(function () {
                self.columns.push(new DataGridColumn(this));
            });
        }
        self.tbody().children('tr').each(function () {
            var row = {};
            $(this).children().each(function () {
                if (data.length <= length) {
                    data.push(this.innerHTML);
                }
            });
            data.push(row);
        });
        return data;
    },
    //
    // Initialise headers when supplied in the options object.
    _initHeaders = function (self) {
        var columns = [],
            tr = TRH.cloneNode(false);
        //
        self.columns = columns;
        if (_.isNumber(self.options.columns)) {
            var num = parseInt(self.options.columns, 10);
            self.options.columns = [];
            for(var i=0; i<num; i++) {
                self.options.columns.push(new DataGridColumn());
            }
        }
        _(self.options.columns).forEach(function (column) {
            if (!(column instanceof DataGridColumn)) {
                if (typeof(column) === 'string') {
                    column = {name: column};
                }
                column = new DataGridColumn(column);
            }
            tr.appendChild(column.th[0]);
            columns.push(column);
        });
        self.thead().append($(tr));
    },
    //
    _add_extensions = function (self) {
        var extensions = self.extensions,
            options = self.options;
        self.extensions = {};
        _(extensions).forEach(function (Extension) {
            _(Extension.prototype.options).forEach(function (value, name) {
                if (!(name in options)) {
                    options[name] = value;
                }
            });
            self.extensions[Extension.prototype.name] = new Extension(self);
        });
    },
    //
    // Register events to this instance,
    // called during initialisation
    _register_events = function (self) {
        _.extend(self, {
            onReady: new Event('ready', self),
            onScroll: new Event('scroll', self),
            onSort: new Event('sort', self),
            // Fired when on a click event
            onClick: new Event('click', self),
            // Fired when a new column is added to the datagrid
            onColumn: new Event('column', self)
        });
    };

//
});