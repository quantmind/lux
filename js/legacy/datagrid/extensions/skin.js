    // Perform client side column sorting
    DataGrid.Extension('skin', {
        //
        defaults: {
            styles: {
                'plain': '',
                'table': 'table',
                'grid': 'grid'
            },
            //
            style: 'table',
            //
            skin: 'default',
            //
            rowHeight: 20,
            //
            minWidth: 30,
        },
        //
        init: function (g) {
            var self = this;
            //
            g.style = function (name) {
                self.style(g, name);
            };
            //
            g.setSkin(g.options.skin);
            //
            g.style(g.options.style);
            //
            if (g.options.rowHeight)
                this._createCssRules(g);
        },
        //
        // Set the style of the table
        style: function (g, name) {
            if (g.options.styles[name] !== undefined) {
                _(g.options.styles).forEach(function (cn) {
                    g.elem.removeClass(cn);
                });
                g.elem.addClass(g.options.styles[name]);
            }
        },
        //
        _createCssRules: function (g) {
            var cellHeightDiff = 0,
                uid = g.elem[0].id,
                rowHeight = (g.options.rowHeight - cellHeightDiff),
                rules = [
                    "#" + uid + " .row { height:" + g.options.rowHeight + "px; }",
                    "#" + uid + " .row > td { height:" + rowHeight + "px; }"
                  ];
                if (g.options.minWidth) {
                    rules.push('#' + uid + " .row > th { min-width:" + g.options.minWidth + "px; }");
                }
            g.addStyle(rules);
        }
    });