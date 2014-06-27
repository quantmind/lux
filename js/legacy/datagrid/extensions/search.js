    // Search box for full text search
    //
    datatable.extend('search', {
        //
        options: {
            search: false,
            input_delays: 1000,
            search_input: null
        },
        //
        init: function (g) {
            var self = this,
                o = this.options,
                value;
            //
            if (o.search) {
                var input = o.search_input,
                    sPreviousSearch = null,
                    oTimerId;

                if (!input) {
                    input = $(document.createElement('input'));
                }
                input.attr('name', o.search);
                input.unbind('keyup').bind('keyup', function () {
                    value = input[0].value;
                    if (sPreviousSearch === null || sPreviousSearch !== value) {
                        window.clearTimeout(oTimerId);
                        oTimerId = null;
                        sPreviousSearch = value;
                        if (value) {
                            oTimerId = window.setTimeout(function () {
                                self.search(;
                            }, o.input_delay);
                        }
                    }
                });
            }
        }
    });