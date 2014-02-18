    //
    // Dialog for editing Content
    // ------------------------------------

    //
    // Pop up dialog for editing content within a block element.
    // ``self`` is a positionview object.
    var edit_content_dialog = function (options) {
        var dialog = web.dialog(options.contentedit),
            page_limit = options.page_limit || 10,
            // The grid containing the form
            grid = $(document.createElement('div')).addClass('columns'),
            content_fields = $(document.createElement('div')).addClass('content-fields column pull-left span8'),
            content_data = $(document.createElement('div')).addClass(
                'content-data column').css('padding-left', content_fields.width()),
            //
            fieldset_selection = $(document.createElement('fieldset')).addClass(
                'content-selection').appendTo(content_fields),
            fieldset_dbfields= $(document.createElement('fieldset')).addClass(
                dbfields).appendTo(content_fields),
            fieldset_submit= $(document.createElement('fieldset')).addClass(
                'submit').appendTo(content_fields),
            db = Content._meta.fields,
            //
            // Build the form container
            form = web.form(),
            //
            // Create the select element for HTML wrappers
            wrapper_select = web.create_select(cms.wrapper_types()).attr(
                'name', 'wrapper'),
            color_select = web.create_select(lux.web.SKIN_NAMES).attr(
                'name', 'style'),
            //
            // create the select element for content types
            content_select = web.create_select(cms.content_types()).attr(
                'name', 'content_type'),
            //
            content_title,
            //
            content_id,
            //
            block;
            //
        form._element.append(content_fields).append(content_data).appendTo(grid);
        form.add_input(wrapper_select, {
            fieldset: fieldset_selection
        });
        form.add_input(color_select, {
            fieldset: fieldset_selection
        });
        form.add_input(content_select, {
            fieldset: fieldset_selection
        });
        form.add_input('submit', {
            value: 'Done',
            fieldset: fieldset_submit
        });
        //
        // database fields
        content_id = db.id.add_to_form(form);
        content_title = db.title.add_to_form(form);
        db.keywords.add_to_form(form).select({
            tags: [],
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
        // Detach data fields
        fieldset_dbfields.detach();
        //
        dialog.body()
            .append(grid)
            .addClass('edit-content')
            .bind('close-plugin-edit', function () {
                dialog.destroy();
            });
        //
        // Apply select
        web.select(wrapper_select, {'placeholder': 'Choose a container'});
        web.select(content_select, {'placeholder': 'Choose a content'});
        color_select.select({
            placeholder: 'Choose a skin',
            formatResult: skin_color_element,
            formatSelection: skin_color_element,
            escapeMarkup: function(m) { return m; }
        }).change(function () {
            block.skin = this.value;
        });
        //
        // AJAX Content Loading
        if (options.content_url) {
            content_title.select({
                placeholder: 'Search content',
                minimumInputLength: 2,
                id: function (data) {
                    return data.title;
                },
                initSelection: function (element, callback) {
                    var value = element.val();
                    callback({'title': value});
                },
                formatResult: function (data, c, query) {
                    if (!data.title) {
                        // This must be the first entry
                        data.title = query.term;
                    }
                    return '<p>' + data.title + '</p>';
                },
                formatSelection: function (object, container) {
                    if (object.id === -1) {
                        content_id.val('');
                    } else if (object.id) {
                        $.ajax({
                            url: options.content_url + '/' + object.id,
                            success: function (model_data) {
                                var data = model_data,
                                    Content = cms.content_type(data.content_type);
                                if (model_data.data) {
                                    data = model_data.data;
                                    delete model_data.data;
                                    _.extend(data, model_data);
                                }
                                block.content = new Content(data);
                                block.content.update_form(form._element);
                            }
                        });
                    }
                    return object.title;
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
                    results: function (data, page) {
                        // Insert the null element at the beginning so that we
                        // put the typed test as an option to create a new
                        // content
                        data.splice(0, 0, {title: '', id: -1});
                        return {
                            results: data,
                            more: _.size(data)-1 === page_limit
                        };
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
                    fields = lux.fields_from_array(arr),
                    wrapper = fields.wrapper;
                delete fields.wrapper;
                content.replace(fields);
                block.wrapper = wrapper;
                block.set(content);
                dialog.fadeOut();
                return false;
            }
        });
        //
        // Change content type in the view block
        content_select.change(function (e) {
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
                block.log(block + ' changed content type to ' + block.content);
                block.content_history[block.content._meta.name] = block.content;
                if (block.content._meta.persistent) {
                    fieldset_selection.after(fieldset_dbfields);
                    block.content.update_form(form._element);
                } else {
                    fieldset_dbfields.detach();
                }
                // Get the form for content editing
                content_data.html('');
                block.content.get_form(function (cform) {
                    content_data.append(cform._element.children());
                });
            } else if (name) {
                web.logger.error('Unknown content type ' + name);
            } else {
                fieldset_dbfields.detach();
                content_data.html('');
            }
            if (block.wrapper !== wrapper_select.val()) {
                wrapper_select.val(block.wrapper).trigger('change');
            }
        });
        //
        // Change container
        wrapper_select.change(function () {
            block.wrapper = this.value;
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

    var skin_color_element = function (state) {
        if (!state.id) return state.text; // optgroup
        return "<div class='colored " + state.id + "'>" + state.text + "</div>";
    };
