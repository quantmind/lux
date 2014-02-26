
    var CheckboxColumn = DataGridColumn.extend({

    });

    // Add a checkbox column as the first column in the datagrid
    DataGrid.Extension('checkboxSelector', {
        //
        defaults: {
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
        defaults: {
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