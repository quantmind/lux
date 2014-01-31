    // Perform client side column sorting
    DataGrid.Extension('skin', {
        options: {
            styles: {
                'plain': '',
                'table': 'table',
                'grid': 'table-grid'
            },
            style: 'table',
            skin: 'default'
        },
        init: function (g) {
            var self = this;
            g.skin = function (name) {
                self.skin(g, name);
            };
            g.style = function (name) {
                self.style(g, name);
            };
            g.skin(g.options.skin);
            g.style(g.options.style);
        },
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
                each(g.options.styles, function (cn) {
                    g.elem.removeClass(cn);
                });
                g.elem.addClass(g.options.styles[name]);
            }
        }
    });