    //
    // ## Inline Editing

    //
    // Inline editing is implemented with a pop up dialog
    // within a [content view](#content-view) element.

    var edit_content_dialog = function (options) {
        var dialog = new lux.Dialog(options.contentedit),
            page_limit = options.page_limit || 10,
            // The grid containing the form
            grid = $(document.createElement('div')).addClass('columns'),
            content_fields = $(document.createElement('div')).addClass(
                'content-fields column pull-left span8'),
            content_data = $(document.createElement('div')).addClass(
                'content-data column').css('padding-left', content_fields.width()+20),
            //
            fieldset_content = $(document.createElement('fieldset')).addClass(
                content_type).appendTo(content_fields),
            fieldset_dbfields= $(document.createElement('fieldset')).addClass(
                dbfields).appendTo(content_fields),
            fieldset_submit= $(document.createElement('fieldset')).addClass(
                'submit').appendTo(content_fields),
            //
            // Build the form container
            form = new lux.Form(),
            //
            // Create the select element for HTML wrappers
            wrapper_select,
            content_select,
            content_id,
            //
            block;
            //
        form.elem.append(content_fields).append(content_data).appendTo(grid);
        form.addFields(Content._meta.fields);
        form.addSubmit({
            text: 'Done',
            fieldset: fieldset_submit
        });
        form.render();
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
        // Change skin event
        form.elem.find('[name="skin"]').change(function () {
            block.skin = this.value;
        });
        //
        content_id = fieldset_dbfields.find('[name="id"]');
        content_select = fieldset_content.find('[name="content_type"]');
        wrapper_select = fieldset_content.find('[name="wrapper"]').change(function () {
            block.wrapper = this.value;
        });
        //
        // AJAX Content Loading is available when the ``options`` object
        // contain the ``content_url``
        if (options.content_url) {
            fieldset_dbfields.find('[name="title"]').Select({
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
                                block.content.updateForm(form.elem);
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
                    fieldset_content.after(fieldset_dbfields);
                    block.content.updateForm(form.elem);
                } else {
                    fieldset_dbfields.detach();
                }
                // Get the form for content editing
                content_data.html('');
                var cform = block.content.getForm();
                content_data.append(cform.render().elem.children());
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
