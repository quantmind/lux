    //
    web.extension('content-edit', {
        selector: 'form.content-edit',
        //
        decorate: function () {
            var edit = this,
                form = edit.element();
            form.find('textarea.preview').each(function () {
                edit._text_area_with_preview($(this));
            });
        },
        //
        _text_area_with_preview: function (elem) {
            var id = this.id(),
                write_id = id + '_write',
                preview_id = id + '_preview';
                write = elem.wrap('<div id="' + preview_id + '"/>'),
                preview = $(document.createElement('div')).attr('id', preview_id),
                tags = write.wrap('<div/>'),
                ul = $(document.createElement('ul')),
                tags.append(preview);
        }
    });