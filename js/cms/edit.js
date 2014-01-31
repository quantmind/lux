
    var inner_dialog = "<div class='content-editor'>".concat(
            "<div class='editor'>",
            "<div class='preview'>",
            "</div>",
            "</div>",
            "</div>");

    // Edit content by opening a dialog
    var edit_content_dialog = function (self, options) {
        if (self._content_dialog) {
            return self._content_dialog;
        }
        options = options || {};
        var dialog = web.dialog({
                modal: true,
                movable: true,
                fullscreen: true,
                title: 'Edit Content'
            }),
            editor = $(document.createElement('div')).addClass('editor'),
            preview = $(document.createElement('div')).addClass('preview'),
            container = $(document.createElement('div')).append(editor).append(preview),
            //
            // Create the selct element for HTML wrappers
            wrapper_select = web.create_select(cms.wrapper_types(),
                    {placeholder: 'Select a container'}),
            //
            // create the select element for content types
            content_select = web.create_select(cms.content_types(),
                    {placeholder: 'Select a Content'}),
            top = $(document.createElement('div')).addClass('top'
                    ).append(wrapper_select).append(content_select).appendTo(editor),
            edit_form = $(document.createElement('div'));
        //
        dialog.body()
            .append(container)
            .addClass('edit-content')
            .bind('close-plugin-edit', function () {
                dialog.destroy();
            });
        //
        // Change content type
        content_select.element().change(function () {
            var name = $(this).val();
            self.content = self.content_history[name];
            if (!self.content) {
                var ContentType = cms.content_type(name);
                if (ContentType) {
                    self.content = new ContentType();
                }
            }
            if (self.content) {
                web.logger.info(self + ' changed content type to ' + self.content);
                self.content_history[self.content._meta.name] = self.content;
                self.content.edit(self, container);
            } else {
                web.logger.error('Unknown content type ' + name);
            }
        });
        //
        // Change container
        wrapper_select.element().change(function () {

        });
        //
        if (self.content) {
            self.content_history[self.content._meta.name] = self.content;
            content_select.element().val(self.content._meta.name).trigger('change');
        }
        //
        return dialog;
    };
    //
    // The Html element for editing a content block
    var edit_content_element = function (self) {
        var container = $(document.createElement('div')),
            toolbar = $(document.createElement('div'))
                        .addClass('cms-position-toolbar').appendTo(container),
            group = $(document.createElement('div'))
                        .addClass('btn-group right').appendTo(toolbar),
            button = parent.dialog.create_button({icon: 'edit', size: 'mini'})
                        .click(function () {
                            self.edit_content();
                        }).appendTo(group),
            title = $(document.createElement('span')).prependTo(toolbar);
        this.button_group = group;
        this.title = title;
        container.appendTo(self.elem.parent());
        this.elem.addClass('preview').appendTo(container);
        this._container = container;
        this.content_history = {};
    };
