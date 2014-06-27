    

    web.extension('datagrid', {
        //
        selector: '.datagrid',
        //
        defaultElement: 'div',
        //
        options: {
            columns: [],
            classes: {
                top: 'ui-widget-header',
                thead: 'hd',
                label: 'label',
                panel_group: 'panel-group'
            },
            inputs: {
                delay: 500
            },
            layout: {
                // show footer only if it is in the original table.
                // Set to false or true to force behaviour
                footer: null,
                header: true,
                // The top of the table
                top: null,
             // bottom of the table
                bottom: null
            },
            source: null // could be ajax, websocket
        },
        cssvariables: {
            padding: '4px 6px',
            head: {
                font_weight: null,
                font_size: null
            }
        },
        // table constructor
        init: function () {
            this.datagrid = new DataGrid(this.element());
        },
        // Create the table placehoder
        create_placeholder: function (elem) {
            if(elem.is('table')) {
                var c = $('<div>'),
                    classes = elem[0].className; 
                elem.before(c);
                elem[0].className = '';
                return c.append(elem).addClass(classes);
            } else {
                return elem;
            }
        },
        // Set table headers
        setHeaders: function (headers_) {
            var self = this,
                headers = headers_ || self.options.columns,
                thead = self._thead(),
                new_headers = [],
                obj_headers = {},
                tr;
            function _head_class(col, th) {
                var text = col.label,
                    code = col.code || text;
                col.code = code.replace(' ', '-').toLowerCase();
                col.class_name = 'col-' + col.code;
                th.addClass(col.class_name)
                  .addClass(self.prefixed('header'))
                  .data('header', col.code);
                return col;
            }
         // No headers, check if available on the html
            if (headers.length === 0) {
                tr = thead.last('tr');
                if (tr.length) {
                    tr.find('th').each(function () {
                        var th = $(this),
                            text = th.html(),
                            col = {label: text};
                        _head_class(col, th);
                        new_headers.push(col.code);
                        obj_headers[col.code] = col;
                    });
                }
            } else {
                thead.html('');
                tr = $(document.createElement('tr')).appendTo(thead);
                $.each(headers, function (i, col) {
                    var th = $(document.createElement('th')),
                        code;
                    if(!$.isPlainObject(col)) {
                        col = {label: col};
                    } else {
                        col = $.extend(true, {}, col);
                    }
                    if (!col.label) {
                        col.label = col.code || 'header ' + (i+1);
                    }
                    _head_class(col, th);
                    th.html(col.label).appendTo(tr);
                    new_headers.push(col.code);
                    obj_headers[col.code] = col;
                });
            }
            this.data.headers = {
                codes: new_headers,
                data: obj_headers,
                at: function (index) {
                    return this.data[this.codes[index]];
                }
            };
        },
        //
        _row_entry: function (td, head) {
            if (!head) {
                td.remove();
            } else {
                return td.addClass(head.class_name)
                        .addClass(this.prefixed('cell'));
            }
        },
        // Set data to the table
        setData: function (data) {
            var self = this,
                tbody = this._tbody(),
                headers = this.data.headers;
            // No data provided
            if(lux.isnothing(data)) {
                tbody.find('tr').each(function () {
                    $(this).find('td').each(function (col) {
                        self._row_entry($(this), headers.at(col));
                    });
                });
            } else {
                tbody.html('');
                this.update(data);
            }
        },
        // Update data
        update: function (data) {
            var self = this,
                tbody = this._tbody(),
                headers = this.data.headers;
            //
            if (!data) {
                return;
            }
            function _td(head, value) {
                var td = $(document.createElement('td')).html(value);
                return self._row_entry(td, head);
            }
            //
            $.each(data, function (row, row_data) {
                var tr = $(document.createElement('tr'));
                // We have two options for row_data: The first one it is an object
                if($.isPlainObject(row_data)) {
                    $.each(headers.codes, function (i, code) {
                        var td = _td(headers.data[code], row_data[code] || '');
                        if(td) {
                            tr.append(td);
                        }
                    });
                } else if($.isArray(row_data)) {
                    $.each(row_data, function (col, value) {
                        var td = _td(headers.at(col), value);
                        if(td) {
                            tr.append(td);
                        }
                    });
                }
                tr.appendTo(tbody);
            });
        },
        // Set visibility for a column
        _setColVisibility: function (column_code_or_index, show) {
            var headers = this.data.headers,
                col, index, selector, position, i;
            if(typeof(code_or_index) === 'number') {
                index = column_code_or_index;
                col = headers.at(index);
            } else {
                col = this.data.headers.data(column_code_or_index);
                index = headers.indexOf(column_code_or_index);
            }
            // Nothing to do
            if (!col || col.visible === show) {
                return;
            }
            selector = '.' + col.class_name;
            //
            if (show) {
                position = 0;
                for(i = 0; i < index; i++) {
                    if (headers.at(i).visible) {
                        position++;
                    }
                }
                
            } else {
                // remove td from table and store them in the col object
                col.hiddens = {head: this._thead().find(selector).remove(),
                               body: this._tbody().find(selector).remove(),
                               foot: this._tfoot().find(selector).remove()};
            }
            col.visible = show;
        },
        //
        _table: function () {
            return this.container().find('table');
        },
        _thead: function () {
            return this.container().find('thead');
        },
        _tbody: function () {
            return this.container().find('tbody');
        },
        _head: function (elem) {
            var h = this.data.headers.data[elem];
            if(!h) {
                elem = $(elem).closest('th');
                if (elem.length) {
                    h = this.data.headers.data[elem.data('header')];
                }
            }
            return h;
        },
        _inputName: function (name) {
            return name;
        },
        _layout: function (elem, rows) {
            // add rows to an element (either the top or bottom pannel)
            var self = this,
                classes = self.options.classes;
            function row_bit(elems) {
                var c = $(document.createElement('div'));
                if(typeof(elems) === 'string') {
                    elems = [elems];
                }
                $.each(elems, function(i, name) {
                    var bit = $(document.createElement('div')).appendTo(c),
                        layout = self.layout[name];
                    if(typeof(layout) === 'function') {
                        layout = layout.apply(self);
                    }
                    bit.append($(layout));
                });
                return c;
            }
            // Loop over rows
            $.each(rows, function (i, row) {
                // the row div
                var row_div = $(document.createElement('div')).addClass(classes.panel_group).appendTo(elem);
                if(row.left) {
                    row_div.append(row_bit(row.left).css({float: 'left'}));
                }
                if(row.right) {
                    row_div.append(row_bit(row.right).css({float: 'right'}));
                }
            });
        }
});