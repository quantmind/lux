    //
    // Dialog for editing Content
    // ------------------------------------

    //
    // Pop up dialog for editing content within a block element.
    // ``self`` is a positionview object.
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
            grid = web.grid(),
            preview = $(document.createElement('div')).addClass('preview'),
            form = web.form(),
            //
            // Create the select element for HTML wrappers
            wrapper_select = web.create_select(cms.wrapper_types()),
            //
            // create the select element for content types
            content_select = web.create_select(cms.content_types()),
            //
            content_search = web.create_select(),
            //
            search = $(document.createElement('fieldset')).addClass('search').hide();
            //
        form.add_input(wrapper_select);
        form.add_input(content_select);
        search.append(content_search);
        form._element.append(search);
        grid.column(0).append(form._element);
        grid.column(1).append(preview);
        //
        dialog.body()
            .append(grid._element)
            .addClass('edit-content')
            .bind('close-plugin-edit', function () {
                dialog.destroy();
            });
        //
        // Apply select
        web.select(wrapper_select);
        web.select(content_select);
        //
        // Change content type
        content_select.change(function () {
            var name = this.value;
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
                if (self.content._meta._persistent) {
                    search.show();
                } else {
                    search.hide();
                }
                self.content.edit(self, form);
            } else {
                web.logger.error('Unknown content type ' + name);
            }
        });
        //
        // Change container
        wrapper_select.change(function () {

        });
        //
        if (self.content) {
            self.content_history[self.content._meta.name] = self.content;
            content_select.val(self.content._meta.name).trigger('change');
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
