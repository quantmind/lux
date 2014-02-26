
    var DataGridRow = exports.DataGridColumn = lux.createView('datagridrow', {
        jQuery: true,
        //
        tagName: 'tr',
        //
        initialise: function (options) {
            var columns = options.datagrid ? options.datagrid.columns : null,
                model = this.model;
            if (columns) {
                for (var j=0; j<columns.length; j++) {
                    var col = columns[j],
                        cell = new Cell({column: col, 'model': model});
                    this.elem.append(cell.elem);
                }
            }
        }
    });
