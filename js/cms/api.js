    //
    // CRUD API Extension
    // ------------------------------
    //
    // Check for an ``api`` key in the ``html`` document ``data`` attribute.
    // If available, the api key contains the ``url`` for the site API.
    // It build the ``datatable`` ``Content``.
    lux.web.extension('api', {
        selector: 'html',
        //
        decorate: function () {
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
            form.add_input('checkbox', {
                name: 'editable',
                label: 'Editable'
            });
            form.add_input('checkbox', {
                name: 'footer',
                label: 'Display footer'
            });
            form.add_input('submit', {value: 'Done'});
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
        }
    });
