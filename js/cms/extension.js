    //
    //  lux web CMS extension
    //  --------------------------------
    //
    //  This is the javascript handler of ``lux.extensions.cms``.
    //  Updates to the backend are either via a websocket or ajax requests.
    lux.web.extension('cms', {
        selector: 'div.cms-page',
        //
        options: {
            editing: false,
            // backend url used to communicate with backend server
            // when updating & creating content as well as when
            // repositioning it
            backend_url: null,
            //
            // content url is used for AJAX retrieval of database contents
            content_url: null,
            //
            // icon for the button which add a new row in a grid
            add_row_icon: 'columns',
            // icon for the button which add a new block in a column
            add_block_icon: 'plus',
            //
            skin: 'control',
            //
            row_control_class: 'add-row',
            //
            columns: 24,
            //
            // Options for the dialog controlling page inputs
            page: {
                collapsable: true,
                collapsed: true,
                class_name: 'control',
                skin: 'inverse',
                buttons: {
                    size: 'default'
                }
            },
            // Options for the dialog controlling one grid
            grid: {
                collapsable: true,
                skin: null,
                class_name: 'control',
                buttons: {
                    size: 'default'
                }
            },
            // Options for the row dialog
            row: {
                closable: true,
                collapsable: true,
                skin: 'default',
                size: 'mini',
                dragdrop: false,
                dropzone: 'row-control'
            },
            // Options for the block dialog
            block: {
                closable: true,
                collapsable: true,
                skin: 'primary',
                size: 'mini',
                dragdrop: true,
                dropzone: 'block-control'
            },
            // Options for content editing dialog
            contentedit: {
                modal: true,
                movable: true,
                fullscreen: true,
                autoOpen: false,
                title: 'Edit Content',
                fade: {duration: 20},
                closable: {destroy: false}
            }
        },
        //
        // The decorator called by ``lux.web``
        decorate: function () {
            var self = this,
                options = self.options,
                elem = self.element(),
                control = $('.cms-control');
            // In editing mode, set-up grids
            if (options.editing) {
                //self._handle_close();
                elem.addClass('editing');
                //
                // Create backend
                self.backend = web.backend({
                    host: options.backend_url,
                    hartbeat: 5
                });
                //
                lux.cms.set_transport(self.backend.socket);
                lux.cms.get(options.editing, {
                    success: function (page) {
                        self.view = new PageView(page[0], self);
                        self.view.render();
                    }
                });
                //
                self._setup_api();
            } else {
                self.view = new PageView(null, this);
                self.view.render();
            }
        },
        //
        _setup_api: function () {
            this.url = this.element().data('api');
            if (!this.url) {
                this.on_sitemap();
            } else {
                var self = this;
                $.ajax(this.url, {
                    dataType: 'json',
                    success: function (data, status, xhr) {
                        self.on_sitemap(data);
                    }
                });
            }
        },
        //
        // When the api sitemap is available, this method setup the
        // datatable content type.
        on_sitemap: function (sitemap) {
            var self = this,
                // Dictionary of models urls and fields
                models = {},
                groups = null;
            this.models = models;
            //
            lux.cms.create_content_type('datatable', {
                model_title: 'Data Grid',
                //
                render: function (container) {
                    var elem = this.get('jQuery');
                    if (!elem) {
                        elem = $(document.createElement('div')).data({
                            colHeaders: this.get('fields'),
                            ajaxUrl: this.get('url')
                        });
                    }
                    elem.appendTo(container.html(''));
                    require(['datagrid'], function () {
                        lux.web.datagrid(elem);
                    });
                },
                //
                // Once the form is submitted get the fields to store in the
                // model content
                get_form_fields: function (arr) {
                    var data = this._super(arr),
                        api_model = models[data.url];
                    if (api_model) {
                        var columns = [];
                        if (data.fields) {
                            _(data.fields).forEach(function (id) {
                                columns.push(api_model.map[id]);
                            });
                        } else {
                            columns = api_model.fields;
                        }
                        data.fields = columns;
                        return data;
                    } else {
                        return {};
                    }
                },
                //
                get_form: function () {
                    // The select model is not yet available, create it.
                    if(!groups && sitemap) {
                        groups = self.create_groups(sitemap);
                    }
                    if (groups) {
                        return self.create_form(groups);
                    }
                }
            });
        },
        //
        // sitemap is a list of api section handlers
        create_groups: function (sitemap) {
            var groups = [],
                models = this.models;
            //
            // Add options to the model select widgets
            _(sitemap).forEach(function (section) {
                var group = $(document.createElement('optgroup')).attr('label', section.name);
                groups.push(group);
                _(section.routes).forEach(function (route) {
                    $(document.createElement('option'))
                             .val(route.api_url).html(route.model).appendTo(group);
                    // Add the route to the models object
                    models[route.api_url] = route;
                });
            });
            return groups;
        },
        //
        // Create the form for adding a data grid
        create_form: function (sessions) {
            var form = lux.web.form(),
                select_model = form.add_input('select', {name: 'url'}),
                models = this.models;
            select_model.append($(document.createElement('option')).html('Choose a model'));
            _(sessions).forEach(function (group) {
                select_model.append(group);
            });
            // Create the fields multiple select
            var fields = form.add_input('select', {
                multiple: 'multiple',
                name: 'fields'
            }).select2({
                placeholder: 'Select fields to display'
            });
            form.add_input('input', {
                type: 'checkbox',
                name: 'editable',
                label: 'Editable'
            });
            form.add_input('input', {
                type: 'checkbox',
                name: 'footer',
                label: 'Display footer'
            });
            //
            // When a model change, change the selction as well.
            select_model.select2().change(function (e) {
                var url = $(this).val(),
                    model = models[url],
                    options = model.options;
                fields.val([]).trigger("change");
                fields.children().remove();
                if (options) {
                    _(options).forEach(function (option) {
                        fields.append(option);
                    });
                } else {
                    model.options = options = [];
                    model.map = {};
                    _(models[url].fields).forEach(function (field) {
                        var option = $(document.createElement('option'))
                                        .val(field.code).html(field.name);
                        model.map[field.code] = field;
                        options.push(option);
                        fields.append(option);
                    });
                }
            });
            return form;
        },
        //
        _handle_close: function () {
            $(window).bind('beforeunload', function (e) {
                e.preventDefault();
                return false;
            });
        }
    });

    //  lux web grid CMS decorator
    //  -----------------------------------------
    //
    lux.web.extension('grid', {
        defaultElement: 'div',
        //
        options: {
            template: 'Half-Half',
            columns: 24
        },
        //
        decorate: function () {
            var template = ROW_TEMPLATES.get(this.options.template),
                options = this.options,
                elem = this.element();
            if (!template) {
                this.options.template = 'Half-Half';
                template = ROW_TEMPLATES.get(this.options.template);
            }
            this.template = template;
            elem.addClass('row grid'+this.options.columns);
            _(this.template).forEach(function (width) {
                var span = width*options.columns,
                    col = $(document.createElement('div')).addClass('column span'+span);
                elem.append(col);
            });
        },
        //
        // Retrieve the jQuery element correspondint to the column at ``index``
        column: function (index) {
            var children = this._element[0].childNodes;
            return $(children[index]);
        }
    });
