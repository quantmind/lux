//      Lux Javascript Library - v0.1.0

//      Compiled 2014-01-18.
//      Copyright (c) 2014 - Luca Sbardella
//      Licensed BSD.
//      For all details and documentation:
//      https://github.com/lsbardel/lux

define(['jquery', 'lux-web'], function ($) {
    //
    var each = lux.each;
    //
    lux.web.visual_tests = {};
    lux.web.visual_test = function (test, callable) {
        lux.web.visual_tests[test] = callable;
    };
    //
    lux.web.extension('visual_test', {
        selector: 'div.visual-test',
        decorate: function () {
            var test = lux.web.visual_tests[this.options.test];
            if (test) {
                var grid = lux.web.grid(this.element(), {template: '75-25'}),
                    //logger = $(document.createElement('div')).height(500),
                    panel = $(document.createElement('div')),
                    columns = grid.element().children();
                panel.appendTo(columns[0]);
                //logger.appendTo(columns[1]);
                //lux.web.logger.addElement(logger);
                test.call(panel);
            }
        }
    });
    //
    lux.web.visual_test('dragdrop', function () {
        var elem = $(document.createElement('div')).appendTo(this).width(100).height(100)
                            .css({
                                background: '#0F4FA8',
                                position: 'relative',
                                color: '#fff'
                            }),
            dragdrop = new lux.web.DragDrop({
                dropzone: this,
                onDrag: function (e) {
                    $(this).html('(' + e.originalEvent.clientX + ', ' + e.originalEvent.clientY + ')');
                },
                onDrop: function (elem, e, offset) {
                    dragdrop.reposition(elem, e, offset);
                }
            });
        this.height(500);
        dragdrop.add(elem);
    });
    lux.web.visual_test('sortable', function () {
        var web = lux.web,
            grid = web.grid({template:'33-33-33'}),
            panels = grid.element().children(),
            menu = $(panels[0]),
            container1 = $(panels[1]),
            container2 = $(panels[2]),
            placeholder = $(document.createElement('div')).addClass('alert');
        //
        grid.element().appendTo(this);
            
        var dd = (function () {
            var dragdrop = new lux.web.DragDrop({
                dropzone: '.sortable',
                onDrop: function (elem, e, dd) {
                    dragdrop.moveElement(elem, this);
                }
            }),
            
            add = function (text, container, skin) {
                var alert = web.alert({'message': text, 'skin': skin || 'default'});
                container.append(alert.element().addClass('sortable'));
                dragdrop.add(alert.element());
            };
        
            add('First Item', container1);
            add('Second Item', container1);
            add('Third Item', container1);
            //
            add('First Item', container2, 'primary');
            add('Second Item', container2, 'primary');
            add('Third Item', container2, 'primary');
            return dragdrop;
        }());
        //
        var form = web.form({
            beforeSubmit: function (data) {
                var placeholdre = data;
            }
        });
        form.element().appendTo(menu);
        form.add_input('intput', {
            type:'checkbox',
            label: 'placeholder'
        }).change(function () {
            dd.placeholder($(this).prop('checked') ? placeholder : null);
        });
        //
        this.height(500);
    });
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
    //
    //  Buttons visual tests
    //  -----------------------------
    //
    lux.web.visual_test('buttons', function () {
        var c = this,
            web = lux.web,
            text = function (tag, text) {
                return $(document.createElement(tag)).html(text || '').appendTo(c);
            },
            btngroup = function () {
                return $(document.createElement('div')).addClass('btn-group').appendTo(text('p'));
            };
        
        text('h3', 'Buttons skins');
        each(web.SKIN_NAMES, function (name) {
            var p = text('p');
            p.append(web.create_button({text: name, icon: 'gears', skin:name}));
            p.append(' ');
            p.append(web.create_button({text: name, skin: name}));
        });
        text('h3', 'Buttons sizes');
        each(web.BUTTON_SIZES, function (name) {
            c.append(web.create_button({text: name, icon: 'gears', size: name}));
            c.append(' ');
        });
        text('h3', 'Buttons with tooltip');
        each(web.BUTTON_SIZES, function (name) {
            c.append(web.create_button({
                text: name,
                icon: 'gears',
                size: name,
                title: 'To disply tooltip, set the title atribute and add the tooltip class',
                classes: 'tooltip'
            }));
            c.append(' ');
        });
        
        text('h3', 'Button Groups');
        each(web.BUTTON_SIZES, function (name) {
            c.append(text('h6', name));
            var b = btngroup();
            b.append(web.create_button({icon: 'download-alt', size:name}));
            b.append(web.create_button({icon: 'bar-chart', size:name}));
            b.append(web.create_button({icon: 'dashboard', size:name}));
            b.append(web.create_button({icon: 'print', size:name}));
        });
    });
//
});