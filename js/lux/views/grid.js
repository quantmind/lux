
    var Grid = lux.Grid = lux.createView('grid', {

        initialise: function (options) {
            var self = this;
            this.elem.addClass('grid').addClass('fluid');

            if (options.rows) {
                _(options.rows).forEach(function (row) {
                    self.addRow(row);
                });
            }
        },
        //
        addRow: function (row) {
            var elem = $(document.createElement('div')).addClass(
                'row').addClass('grid24').appendTo(this.elem);
            //
            _(row).forEach(function (col) {
                var size = 'span' + col;
                elem.append($(document.createElement('div')).addClass(
                    'column').addClass(size));
            });
            return elem;
        }
    });