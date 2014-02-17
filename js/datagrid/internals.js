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
            tr = TR.cloneNode(false),
            cols = self.options.columns;
        //
        self.columns = columns;
        if (_.isNumber(cols)) {
            var num = parseInt(cols, 10);
            cols = [];
            for(var i=0; i<num; i++) {
                cols.push(new DataGridColumn());
            }
        }
        _(cols).forEach(function (column) {
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
