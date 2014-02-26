    /**
     * Add hover to datagrid
     */
    DataGrid.Extension('hover', {
        //
        classes: {
            hover: 'hover'
        },
        //
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