    //
    //  Buttons visual tests
    //  -----------------------------
    //
    lux.web.visual_test('Buttons', function (self) {
        var c = this,
            web = lux.web,
            btngroup = function (options) {
                return web.button_group(options).appendTo(text('p'));
            };

        self.text('h3', 'Buttons skins');
        _(web.SKIN_NAMES).forEach(function (name) {
            var p = text('p');
            p.append(web.create_button({text: name, icon: 'gears', skin:name}));
            p.append(' ');
            p.append(web.create_button({text: name, skin: name}));
        });
        self.text('h3', 'Buttons sizes');
        _.each(web.BUTTON_SIZES, function (name) {
            c.append(web.create_button({text: name, icon: 'gears', size: name}));
            c.append(' ');
        });
        self.ext('h3', 'Buttons with tooltip');
        _.each(web.BUTTON_SIZES, function (name) {
            c.append(web.create_button({
                text: name,
                icon: 'gears',
                size: name,
                title: 'To disply tooltip, set the title atribute and add the tooltip class',
                classes: 'tooltip'
            }));
            c.append(' ');
        });

        self.text('h3', 'Button Groups');
        _.each(web.BUTTON_SIZES, function (name) {
            c.append(text('h6', name));
            var b = btngroup();
            b.append(web.create_button({icon: 'download', size:name}));
            b.append(web.create_button({icon: 'bar-chart-o', size:name}));
            b.append(web.create_button({icon: 'dashboard', size:name}));
            b.append(web.create_button({icon: 'print', size:name}));
        });

        text('h3', 'Vertical Button Groups');
        _.each(web.BUTTON_SIZES, function (name) {
            c.append(text('h6', name));
            var b = btngroup({vertical: true});
            b.append(web.create_button({icon: 'download', size:name}));
            b.append(web.create_button({icon: 'bar-chart-o', size:name}));
            b.append(web.create_button({icon: 'dashboard', size:name}));
            b.append(web.create_button({icon: 'print', size:name}));
        });
    });