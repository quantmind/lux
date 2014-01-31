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