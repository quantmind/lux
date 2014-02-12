define(['jquery', 'lux'], function ($) {
    "use strict";
    var web = lux.web,
        exports = {};

    //  Column
    //  ----------------
    //
    //  A column in a ``DataGrid``. It contains the ``th`` element and several
    //  important information about the column.
    var Column = exports.Column = lux.Class.extend({
        init: function (elem) {
            this.th = $(elem);
            var data = this.th.data(),
                html = this.th.html(),
                code = data.code;
            if (!code) {
                code = lux.s4();
                this.th.data('code', code);
            }
            this.name = data.name || html;
            !html && this.th.html(this.name);
            if (!this.th.attr('id')) {
                var g = this.datagrid(),
                    id = g.id() + '-' + code;
                this.th.attr('id', id);
            }
            this.th.data('column', this);
        },
        //
        id: function () {
            return this.th.attr('id');
        },
        // Unique code within the table
        code: function () {
            return this.th.data('code');
        },
        // Retrieve the ``DataGrid`` instance for this ``Column``.
        datagrid: function () {
            var elem = this.th.closest('.datagrid');
            return elem.datagrid('instance');
        },
        //
        index: function () {
            var index = this.th.index();
            return index;
        }
    });

    //  DataGridView
    //  -------------------------
    //
    //  Base and default class for rendring a ``DataGrid`` on a page.
    var DataGridView = exports.DataGridView = lux.Class.extend({
        init: function (g) {
            this.g = g;
        },
        // Render the datagrid by removing the whole inner html of the ``tbody``
        // tag and regenerating it.
        render: function () {
            var g = this.g,
                body = g.tbody(),
                tr, td;
            body.html('');
            _(this.g.data).forEach(function (row, index) {
                tr = $(document.createElement('tr')).appendTo(body);
                if (g.options.rowHeaders) {
                    tr.append($(document.createElement('th')).html(index+1));
                }
                _(row).forEach(function (value) {
                    tr.append($(document.createElement('td')).html(value));
                });
            });
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
    // * ``columns``, list of ``Column``
    // * ``view``, the ``DataGridView`` instance for rending the grid on a page.
    var DataGrid = exports.DataGrid = lux.Class.extend({
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
            // Column headers. If provided this parameter override both ``minColumns``
            // and ``maxColumns``.
            colHeaders: false,
            rowHeaders: false,
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
            var id = container.attr('id');
            if (!id) {
                container.attr('id', 'dg' + lux.s4());
            }
            this.elem = container;
            container.data('datagrid', this);
            this.data = [];
            this.columns = [];
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
            if (!this.options.data) {
                this.initHTML();
            } else {
                this.data = this.options.data;
                delete this.options.data;
            }
            if (this.options.colHeaders) {
                this.initHeaders();
            }
            if (options.rowHeaders) {
                this.show_row_headers();
            }
            if (options.foot) {
                this.show_tfoot();
            }
            this.view = new DataGridView(this);
            this.add_extensions();
            var event = $.Event('datagrid-initialised');
            this.elem.trigger(event);
            if (!event.isDefaultPrevented()) {
                this.render();
            }
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
        // The jQuery ``tbody`` element
        tbody: function () {
            return this.elem.find('tbody');
        },
        // The jQuery ``tfoot`` element
        tfoot: function () {
            return this.elem.find('tfoot');
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
        // Render this ``DataGrid`` if a suitable ``view`` is available.
        render: function () {
            if (this.view) {
                this.view.render();
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
        // Initialise table data from HTML
        initHTML: function () {
            var heads = this.thead().children('tr'),
                self = this,
                cid = this.id();
            if (heads.length > 1) {
                var h = this.thead().children('tr.headers');
                heads = h.length ? h : heads.last();
            }
            heads.children('th').each(function () {
                self.columns.push(new Column(this));
            });
            var length = self.columns.length;
            if (length) {
                this.tbody().children('tr').each(function () {
                    var data = [];
                    $(this).children().each(function () {
                        if (data.length <= length) {
                            data.push(this.innerHTML);
                        }
                    });
                    self.data.push(data);
                });
            }
        },
        // Initialise headers when supplied in the options object.
        initHeaders: function () {
            var columns = this.columns,
                headers = this.headers(),
                map = {},
                col, id, th;
            _(this.columns).forEach(function (col) {
                map[col.id()] = col;
            });
            _(this.options.colHeaders).forEach(function (header) {
                if (typeof(header) === 'string') {
                    header = {name: header};
                }
                id = header.id;
                th = $(document.createElement('th'));
                if (id) {
                    th.attr(id);
                    delete header.id;
                    if (map[id]) {
                        throw new lux.NotImplementedError();
                    }
                } else {
                    col = new Column(th.data(header).appendTo(headers));
                    map[col.id()] = col;
                    columns.push(col);
                }
            });
        },
        //
        add_extensions: function () {
            var self = this;
            this.extensions = {};
            _(this.constructor.prototype.extensions).forEach(function (Extension) {
                var extOptions = Extension.prototype.options,
                    options= self.options;
                if (extOptions) {
                    _(extOptions).forEach(function (value, name) {
                        if (options[name] === undefined) {
                            options[name] = value;
                        }
                    });
                }
                self.extensions[name] = new Extension(self);
            });
        },
        // Gather all input data in the datagrid
        input_data: function () {
            var self = this,
                data = {'field': this.fields()};
            _(self.extensions).forEach(function (ext) {
                ext.input_data(self, data);
            });
            return data;
        },
        // A list of column codes
        fields: function () {
            var fields = [];
            _(this.columns).forEach(function (col) {
                fields.push(col.code());
            });
            return fields;
        }
    });

    var DataGridExtension = lux.Class.extend({
        name: null,
        input_data: function (g, data) {}
    });

    DataGrid.Extension = function (name, attrs) {
        DataGrid.prototype.extensions.push(DataGridExtension.extend(attrs));
    };

    //
    // Perform client side column sorting
    DataGrid.Extension('sorting', {
        options: {
            sortable: false,
            sorting_icon: 'sort',
            sorting_asc_icon: 'sort-down',
            sorting_desc_icon: 'sort-up'
        },
        classes: {
            enabled: 'sortable',
            sorted: 'sorted'
        },
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
                this._enable_sorting(g);
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
    //  Server side data
    //  -----------------------
    DataGrid.Extension('ajax', {
        options: {
            ajaxUrl: null,
            ajaxDataType: 'json',
            ajaxMethod: 'GET',
            // When true, the data is requested immidiately
            ajaxAutoLoad: true
        },
        //
        init: function (g) {
            if (g.options.ajaxAutoLoad && g.options.ajaxUrl) {
                var self = this;
                g.ajaxLoad = function () {
                    self.ajaxLoad(g);
                };
                g.elem.one('datagrid-initialised', function (e) {
                    e.preventDefault();
                    self.ajaxLoad(g);
                });
            }
        },
        // Load Data via AJAX
        ajaxLoad: function (g) {
            var self = this,
                o = g.options;
            if (o.ajaxUrl) {
                $.ajax(o.ajaxUrl, {
                    dataType: o.ajaxDataType,
                    data: g.input_data(),
                    type: o.ajaxMethod,
                    success: function (data) {
                        g.data = data;
                        g.render();
                    }
                });
            }
        }
    });
    // jQuery extension
    $.fn.datagrid = function (options) {
        var $this = this.first(), // Use only first element from list
            instance = $this.data('datagrid');
        if (options === 'instance') {
            return instance;
        } else {
            if (!instance) {
                instance = new lux.DataGrid($this, options);
            }
            return $this;
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
            this.datagrid = new DataGrid(this.element(), this.options);
        }
    });
    
    return exports;
//
});