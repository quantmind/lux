    //
    //  Datagrid visual tests
    //  -----------------------------
    //
    // Datagrid visual tests
    lux.web.visual_test('datagrid', function () {
        var container = this,
            web = lux.web,
            toolbar = $(document.createElement('div')).addClass('btn-toolbar').appendTo(container),
            size = 'normal',
            style_button = function (style, icon) {
                return web.create_button({
                    text: style,
                    'size': size,
                    'icon': icon,
                    href: style
                });
            },
            skin_choices = function () {
                var group = $(document.createElement('div')).addClass('btn-group');
                each(web.SKIN_NAMES, function (name) {
                    group.append(web.create_button({
                        text: name,
                        skin: name,
                        href: name
                    }));
                });
                group.children().click(function (e) {
                    e.preventDefault();
                    var skin = $(this).html().trim();
                    container.find('.datagrid').each(function () {
                        $(this).datagrid('instance').skin(skin);
                    });
                });
                return group;
            },
            style_choices = function () {
                var group = web.button_group({radio: true});
                group.append(style_button('plain'));
                group.append(style_button('table'));
                group.append(style_button('grid', 'th'));
                group.children().click(function (e) {
                    e.preventDefault();
                    var style = $(this).attr('href');
                    container.find('.datagrid').each(function () {
                        $(this).datagrid('instance').style(style);
                    });
                });
                return group;
            },
            options = $(document.createElement('div')).addClass('btn-group'),
            foot = web.create_button({text:'foot'}).data('toggle', 'button').appendTo(options);
        
        foot.click(function (e) {
            e.preventDefault();
            container.find('.datagrid').each(function () {
                $(this).datagrid('instance').toggle_tfoot();
            });
        });
            
        // Create a plain html table
        var create_html_table = function (headers, data) {
            var table = $(document.createElement('table')),
                tbody = $(document.createElement('tbody')).appendTo(table);
            if (headers) {
                var thead = $(document.createElement('tr')).appendTo(
                        $(document.createElement('thead')).prependTo(table));
                each(headers, function (head) {
                    thead.append($('<th>'+head+'</th>'));
                });
            }
            if (data) {
                each(data, function (row) {
                    var tr = $('<tr></tr>').appendTo(tbody);
                    each(row, function (value) {
                        tr.append($('<td>'+value+'</td>'));
                    });
                });
            }
            return table;
        };
        
        var from_html = function () {
            var html = create_html_table(['first name', 'surname', 'age'],
                                        [['luca', 'sbardella', 41],
                                         ['joshua', 'sbardella', 7],
                                         ['gaia', 'sbardella', 10]]);
            container.append(skin_choices());
            toolbar.append(style_choices());
            toolbar.append(options);
            container.append(html);
            html.datagrid({
                extensions: ['sorting'],
                responsive: true
            });
        };
        
        require(['datagrid'], function () {
            from_html();
        });
    });