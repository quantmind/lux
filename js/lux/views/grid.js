    //
    //  A view for displaying grids
    var
    //
    GridRow = lux.createView('gridrow', {
        //
        initialise: function (options) {
            var self = this;
            this.elem.addClass('row').addClass('grid24');
            //
            _(options.columns).forEach(function (col) {
                var size = 'span' + col;
                self.elem.append($(document.createElement('div')).addClass(
                    'column').addClass(size));
            });
        },
        //
        column: function (index) {
            index = index || 0;
            return this.elem.children().eq(index);
        }
    }),
    //
    Grid = lux.Grid = lux.createView('grid', {
        //
        defaults: {
            type: 'fluid'
        },
        //
        initialise: function (options) {
            var self = this;
            this.elem.addClass('grid').addClass(options.type);

            if (options.rows) {
                _(options.rows).forEach(function (row) {
                    self.addRow(row);
                });
            }
        },
        //
        addRow: function (columns) {
            var row = new GridRow({'columns': columns});
            row.elem.appendTo(this.elem);
            return row;
        },
        //
        row: function (index) {
            index = index || 0;
            return GridRow.getInstance(this.elem.children().eq(index));
        }
    });