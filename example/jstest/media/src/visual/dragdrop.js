
    //  Drag & Drop
    //  --------------------
    web.visual_test('dragdrop', function () {
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