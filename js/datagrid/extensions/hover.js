    /**
     * Add hover to datagrid
     */
    DataGrid.Extension('hover', {
        description: 'Add hover events to the datagrid rows',
        classes: {
            hover: 'hover'
        },
        init: function (g) {
            g.tbody().on('hover', 'tr', function(e) {
                if(e.type === 'mouseenter') {
                    $(this).addClass(g.classes.hover);
                } else {
                    $(this).removeClass(g.classes.hover);
                }
            });
        }
    });