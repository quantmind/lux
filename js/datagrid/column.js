
    //  DataGridColumn
    //  ----------------
    //
    //  A column in a ``DataGrid``. It contains the ``th`` element and several
    //  important information about the column.
    var
    //
    DataGridColumn = exports.DataGridColumn = lux.createView('datagridcolumn', {
        jQuery: true,
        //
        tagName: 'th',
        //
        defaults: {
            resizable: true,
            sortable: false,
            focusable: true,
            selectable: true
        },
        //
        initialise: function (options) {
            this.options = options;
            this.a = $(document.createElement('a'));
            this.elem.empty().append(this.a);
            //
            if (!options.code) {
                options.code = options.name;
            }
        },
        //
        id: function () {
            return this.options.code || this.index();
        },
        //
        label: function () {
            return this.options.name || this.letter();
        },
        //
        // Retrieve the ``DataGrid`` instance for this ``DataGridColumn``.
        datagrid: function () {
            var elem = this.elem.closest('.datagrid');
            return elem.datagrid('instance');
        },
        //
        index: function () {
            return this.elem.index();
        },
        //
        letter: function () {
            return lux.num_to_letter(this.elem.index());
        },
        //
        render: function () {
            var name = this.options.name || this.letter();
            this.a.html(name);
        },
        //
        // Data from input elements within this column
        inputData: function () {
        }
    });