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
            selection,
            search,
            //
            block,
            //
            // Lo-Dash template for the title select element
            titletemplate = _.template('<%= title %> (<%= id %>)'),
            selection_class = 'content-selection',
            dbfields = 'search';
            //
        form.add_input(wrapper_select, {
            fieldset: {Class: selection_class}
        });
        form.add_input(content_select, {
            fieldset: {Class: selection_class}
        });
        content_search = form.add_input('input', {
            name: 'id',
            fieldset: {Class: dbfields}
        });
        //
        // Input for title
        form.add_input('input', {
            fieldset: {Class: dbfields},
            name: 'title',
            placeholder: 'title',
            required: 'required'
        });
        //
        // Input for keywords
        form.add_input('input', {
            fieldset: {Class: dbfields},
            name: 'keywords'
        }).select({
            tags: [],
            placeholder: 'keywords',
            initSelection : function (element, callback) {
                var data = [];
                _(element.val().split(",")).forEach(function (val) {
                    if (val) {
                        data.push({id: val, text: val});
                    }
                });
                callback(data);
            }
        });
        selection = form._element.find('fieldset.' + selection_class);
        search = form._element.find('fieldset.' + dbfields).detach();
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
        // AJAX Content Loading
        if (options.content_url) {
            web.select(content_search, {
                placeholder: 'Search content',
                minimumInputLength: 2,
                initSelection: function (element, callback) {
                    var id = element.val(),
                        text = titletemplate({
                            title: block.content.get('title'),
                            'id': id
                        });
                    callback({'id': id, 'text': text});
                },
                ajax: {
                    url: options.content_url,
                    minimumInputLength: 3,
                    data: function (term, page) {
                        return {
                            q: term, // search term
                            per_page: page_limit,
                            field: ['id', 'title'],
                            content_type: block.content._meta.name,
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
                var content = block.content,
                    fields = content.get_form_fields(arr);
                content.update(fields);
                block.set(content);
                dialog.fadeOut();
                return false;
            }
        });
        //
        // Change content type in the view block
        content_select.change(function () {
            var name = this.value;
            // Try to get the content from the block content history
            block.content = block.content_history[name];
            if (!block.content) {
                var ContentType = cms.content_type(name);
                if (ContentType) {
                    block.content = new ContentType();
                }
            }
            if (block.content) {
                web.logger.info(block + ' changed content type to ' + block.content);
                block.content_history[block.content._meta.name] = block.content;
                if (block.content._meta.persistent) {
                    // Set the form values for the dbcore fields block
                    search.children('input').each(function () {
                        if (this.name) {
                            var val = block.content.get(this.name);
                            lux.set_value($(this), val);
                        }
                    });
                    selection.after(search);
                } else {
                    search.detach();
                }
                // Get the form for content editing
                var cform = block.content.get_form();
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
            block = view;
            if (block.content) {
                block.content_history[block.content._meta.name] = block.content;
                content_select.val(block.content._meta.name).trigger('change');
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
