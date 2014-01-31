    //
    // Perform client side column sorting
    DataGrid.Extension('table', {
        options: {
            model: null
        },
        classes: {
            enabled: 'sortable',
            sorted: 'sorted'
        },
        init: function (g) {
            var options = g.options
                model = options.model,
                colHeaders = options.colHeaders;
            if (!colHeaders) {
                
            }
        }
    });