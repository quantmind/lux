    // jQuery extension
    $.fn.datagrid = function (options) {
        var $this = this.first(), // Use only first element from list
            instance = $this.data(DATAGRID);
        if (options === 'instance') {
            return instance;
        } else {
            if (!instance) {
                instance = new lux.DataGrid($this, options);
            }
            return instance.elem;
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
            var elem = $(this.element()).datagrid(this.options);
            this.datagrid = elem.data(DATAGRID);
        }
    });