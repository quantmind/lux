    //  Datagrid Responsive
    //  -----------------------
    //
    //  Tables that work responsively on small devices. To enable it set
    //  the ``responsive`` options value to ``true``.
    DataGrid.Extension('responsive', {
        //
        init: function (g) {
            if (g.options.responsive) {
                var self = this;
                this.switched = false;
                this._render = g.render;
                g.render = function () {
                    self.render(g);
                };
                $(window).on("resize", function () {
                    self.render(g);
                });
            }
        },
        //
        render: function (g) {
            var width = $(window).width();
            if (width < 767 && !this.switched) {
                this.switched = true;
                var body = g.tbody();
                _(g.columns).forEach(function (col, index) {
                    index += 1;
                    body.find('td:nth-of-type('+index+')').attr(
                                'data-content', col.name);
                });
            } else if (width >= 767 && this.switched) {
                this.switched = false;
                this._render.call(g);
            }
        }
    });