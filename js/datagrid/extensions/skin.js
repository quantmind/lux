    // Perform client side column sorting
    DataGrid.Extension('skin', {
        //
        options: {
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
            g.skin = function (name) {
                self.skin(g, name);
            };
            //
            g.style = function (name) {
                self.style(g, name);
            };
            //
            g.skin(g.options.skin);
            //
            g.style(g.options.style);
            //
            if (g.options.rowHeight)
                this._createCssRules(g);
        },
        //
        skin: function (g, name) {
            var web = lux.web;
            if (web) {
                var skin = web.get_skin(g.elem);
                if (skin !== name) {
                    g.elem.removeClass(skin).addClass(name);
                }
            }
        },
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
                style = $("<style type='text/css' rel='stylesheet' />"
                    ).appendTo($("head")),
                rowHeight = (g.options.rowHeight - cellHeightDiff),
                rules = [
                    "#" + uid + " .row { height:" + g.options.rowHeight + "px; }",
                    "#" + uid + " .row > td { height:" + rowHeight + "px; }"
                  ];
                if (g.options.minWidth) {
                    rules.push('#' + uid + " .row > th { min-width:" + g.options.minWidth + "px; }");
                }

            if (style[0].styleSheet) { // IE
                style[0].styleSheet.cssText = rules.join(" ");
            } else {
                style[0].appendChild(document.createTextNode(rules.join(" ")));
            }
        }
    });