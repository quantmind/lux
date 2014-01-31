    // jQuery extension
    $.fn.datagrid = function (options) {
        var $this = this.first(), // Use only first element from list
            instance = $this.data('datagrid');
        if (options === 'instance') {
            return instance;
        } else {
            if (!instance) {
                instance = new lux.DataGrid($this, options);
            }
            return $this;
        }
    };
    
    //
    web.extension('datagrid', {
        //
        selector: '.datagrid',
        //
        defaultElement: 'div',
        //
        // table constructor
        decorate: function () {
            this.datagrid = new DataGrid(this.element(), this.options);
        }
    });
    
    return exports;