    //  Server side data
    //  -----------------------
    DataGrid.Extension('ajax', {
        options: {
            ajaxUrl: null,
            ajaxDataType: 'json',
            ajaxMethod: 'GET',
            // When true, the data is requested immidiately
            ajaxAutoLoad: true
        },
        //
        init: function (g) {
            if (g.options.ajaxAutoLoad && g.options.ajaxUrl) {
                var self = this;
                g.ajaxLoad = function () {
                    self.ajaxLoad(g);
                };
                g.elem.one('datagrid-initialised', function (e) {
                    e.preventDefault();
                    self.ajaxLoad(g);
                });
            }
        },
        // Load Data via AJAX
        ajaxLoad: function (g) {
            var self = this,
                o = g.options;
            if (o.ajaxUrl) {
                $.ajax(o.ajaxUrl, {
                    dataType: o.ajaxDataType,
                    data: g.input_data(),
                    type: o.ajaxMethod,
                    success: function (data) {
                        g.data = data;
                        g.render();
                    }
                });
            }
        }
    });