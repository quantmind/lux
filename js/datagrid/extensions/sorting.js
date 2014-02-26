    //
    // Perform client side column sorting
    DataGrid.Extension('sorting', {
        //
        defaults: {
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
                _(g.columns).forEach(function (column) {
                    if (column !== col) {
                        self.set_icon(column, g.options.sorting_icon);
                    }
                });
                self.set_icon(column, g.options['sorting_' + g.sortOrder + '_icon']);
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
                    col.elem.removeClass(classes.enabled);
                } else {
                    col.elem.addClass(classes.enabled);
                    self.set_icon(col, g.options.sorting_icon);
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
                var a = col.elem.find('.sortable-toggle');
                if (!a.length) a = ($(document.createElement('a'))
                    ).addClass('sortable-toggle').appendTo(col.elem);
                lux.icon(a, {'icon': icon});
            }
        }
    });