    //
    // Dialog for editing Content
    // ------------------------------------

    //
    // Pop up dialog for editing content within a block element.
    // ``self`` is a positionview object.
    var edit_content_dialog = function (options) {
        var dialog = web.dialog(options.contentedit),
            page_limit = options.page_limit || 10,
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
            content_search,
            //
            search,
            //
            current_content,
            //
            dbfields = 'search';
            //
        form.add_input(wrapper_select);
        form.add_input(content_select);
        content_search = form.add_input('input', {
            type: 'hidden',
            fieldset: {Class: dbfields}
        }).width(212);
        form.add_input('input', {
            fieldset: {Class: dbfields},
            name: 'title',
            placeholder: 'title',
        });
        form.add_input('input', {
            fieldset: {Class: dbfields},
            name: 'keywords'
        }).width(212).select({
            placeholder: 'keywords',
            minimumInputLength: 2,
            ajax: {
                url: options.content_url,
                data: function (term, page) {
                    return {
                        q: term, // search term
                        per_page: page_limit,
                        field: ['keywords'],
                        apikey: options.api_key
                    };
                },
            }
        });
        search = form._element.find('fieldset.' + dbfields).hide();
        grid.column(0).append(form._element);
        grid.column(1).append(preview);
        form.add_input('submit', {value: 'Done', fieldset: {Class: 'submit'}});
        //
        dialog.body()
            .append(grid._element)
            .addClass('edit-content')
            .bind('close-plugin-edit', function () {
                dialog.destroy();
            });
        //
        // Apply select
        web.select(wrapper_select, {'placeholder': 'Choose a container'});
        web.select(content_select, {'placeholder': 'Choose a content'});
        //
        // AJAX Content
        if (options.content_url) {
            web.select(content_search, {
                placeholder: 'Search content',
                minimumInputLength: 2,
                ajax: {
                    url: options.content_url,
                    minimumInputLength: 3,
                    data: function (term, page) {
                        return {
                            q: term, // search term
                            per_page: page_limit,
                            field: ['id', 'title'],
                            content_type: current_content.content._meta.name,
                            apikey: options.api_key
                        };
                    },
                    results: function (data, page) { // parse the results into the format expected by Select2.
                        // since we are using custom formatting functions we do not need to alter remote JSON data
                        return {
                            results: data,
                            more: _.size(data) === page_limit
                        };
                    },
                    formatResult: function (data) {
                        return '<p>' + data.title || 'No title' + '</p>';
                    }
                }
            });
        }
        //
        form.ajax({
            // Aijack form submission.
            // Get the content being edited via the ``edit_content``
            // attribute in the dialog (check the ``PositionView.edit_content`
            // method)
            beforeSubmit: function (arr) {
                var fields = current_content.content.get_form_fields(arr);
                current_content.update(fields);
                position.set(current_content);
                current_content.close();
                return false;
            }
        });
        //
        // Change content type
        content_select.change(function () {
            var name = this.value;
            current_content.content = current_content.content_history[name];
            if (!current_content.content) {
                var ContentType = cms.content_type(name);
                if (ContentType) {
                    current_content.content = new ContentType();
                }
            }
            if (current_content.content) {
                web.logger.info(current_content + ' changed content type to ' + current_content.content);
                current_content.content_history[current_content.content._meta.name] = current_content.content;
                if (current_content.content._meta.persistent) {
                    search.show();
                } else {
                    search.hide();
                }
                // Get the form for content editing
                var cform = current_content.content.get_form();
                form._element.find('.content-form').remove();
                if (cform) {
                    search.after(cform._element.children('fieldset').addClass('content-form'));
                }
            } else {
                web.logger.error('Unknown content type ' + name);
            }
        });
        //
        // Change container
        wrapper_select.change(function () {

        });
        //
        // Inject change content
        dialog.set_current_view = function (view) {
            current_content = view;
            if (current_content.content) {
                current_content.content_history[current_content.content._meta.name] = current_content.content;
                content_select.val(current_content.content._meta.name).trigger('change');
            } else {
                content_select.val('').trigger('change');
            }
        };
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
