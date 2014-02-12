    //
    //  Default CMS Contents
    //  --------------------------------
    //
    //  The following are the default CMS contents shipped with lux ``cms``
    //  distribution. The are created by invoking the
    //  ''lux.cms.create_content_type`` function.

    //
    //  This Content
    //  -------------------
    //
    //  The first a probably most important content type. It represents
    //  the response obtained by the backend server without the cms
    //  system in place.
    lux.cms.create_content_type('contenturl', {
        meta: {
            title: 'Site Content',
        },
        //
        render: function (container) {
            var url = this.get('content_url'),
                elem = this.get('jQuery');
            if (url === 'this') {
                url = lux.web.options.this_url;
            }
            if (elem) {
                container.append(elem);
            } else if (url) {
                container.html('&nbsp;');
                $.ajax(url, {
                    dataType: 'json',
                    success: function (data, status, xhr) {
                        if (data.html) {
                            require(data.requires || [], function () {
                                web.refresh(container.html(data.html));
                            });
                        }
                    }
                });
            } else {
                web.logger.warning('Missing underlying page url and html');
            }
        },
        //
        get_form: function () {
            var form = lux.web.form(),
                select = form.add_input('select', {name: 'content_url'});
            $(document.createElement('option')).val('this').html('this').appendTo(select);
            _(lux.web.options.content_urls).forEach(function (value) {
                $(document.createElement('option')).val(value[1]).html(value[0]).appendTo(select);
            });
            return form;
        }
    });
    //
    //  Blank Content
    //  -------------------
    //
    //  Insert a non-breaking space.
    lux.cms.create_content_type('blank', {
        model_title: 'The content served by the url',
        render: function (container) {
            container.html('&nbsp;');
        }
    });
    //
    //  Markdown
    //  -------------------
    //
    //  Insert a non-breaking space.
    lux.cms.create_content_type('markdown', {
        //
        meta: {
            title: 'Text using markdown',
            persistent: true
        },
        //
        render: function (container) {
            var self = this;
            require(['showdown'], function () {
                var raw = self.get('raw') || '',
                    converter = new Showdown.converter(),
                    html = converter.makeHtml(raw);
                web.refresh(container.html(html));
            });
        },
        //
        get_form: function () {
            var form = lux.web.form();
            form.add_input('textarea', {
                name:'raw',
                value: this.get('raw'),
                rows: 15,
                placeholder: 'Write markdown'
            });
            return form;
        }
    });
    //
    //  Versions
    //  -------------------
    lux.cms.create_content_type('versions', {
        meta: {
            title: 'Versions of libraries'
        },
        //
        render: function (container) {
            var ul = $(document.createElement('ul')).appendTo(container);
            _(web.libraries).forEach(function (lib) {
                ul.append($('<li><a href="' + lib.web + '">' + lib.name +
                            '</a> ' + lib.version + '</li>'));
            });
        }
    });
    //
    //  Datatable
    //  --------------------

    // Data table for models allows to build highly configurable tables or grids
    // which represents collections of models.
    //
    // THis content is available only when lux provide an api for models in the
    // html tag via the ``api`` data key.
    cms.create_content_type('datatable', {
        //
        meta: {
            title: 'Data Grid',
            persistent: true,
            render_queue: [],
            api_info: function (api) {
                this.api = api || {};
                var queue = this.render_queue;
                delete this.render_queue;
                _.each(queue, function (o) {
                    o.content._render(o.container);
                });
            }
        },
        //
        render: function (container) {
            var self = this;
            require(['datagrid'], function () {
                if (self._meta.api === undefined) {
                    self._meta.render_queue.push({
                        content: self,
                        'container': container
                    });
                } else {
                    self._render(container);
                }
            });
        },
        //
        // Once the form is submitted get the fields to store in the
        // model content
        get_form_fields: function (arr) {
            var data = this._super(arr),
                model = this._meta.api.models[data.url];
            if (model) {
                var fields = [];
                if (data.fields) {
                    _(data.fields).forEach(function (id) {
                        fields.push(model.map[id]);
                    });
                } else {
                    fields = model.fields;
                }
                data.fields = fields;
                return data;
            } else {
                return {};
            }
        },
        //
        get_form: function () {
            // The select model is not yet available, create it.
            var api = this._meta.api;
            if (api) {
                if (!api.groups && api.sitemap) {
                    this.create_groups(api);
                }
                if (api.groups) {
                    return this._get_form(api);
                }
            }
        },
        // Internal methods

        //
        // Actually does the datagrid rendering
        _render: function (container) {
            var elem = $(document.createElement('div')).appendTo(container),
                options = this.fields();
            options.colHeaders = options.fields;
            options.ajaxUrl = this._meta.api.url;
            lux.web.datagrid(elem, options);
        },
        //
        // sitemap is a list of api section handlers
        create_groups: function (api) {
            var groups = [],
                models = {};
            //
            // Add options to the model select widgets
            _(api.sitemap).forEach(function (section) {
                var group = $(document.createElement('optgroup')).attr('label', section.name);
                groups.push(group);
                _(section.routes).forEach(function (route) {
                    $(document.createElement('option'))
                             .val(route.api_url).html(route.model).appendTo(group);
                    // Add the route to the models object
                    models[route.api_url] = route;
                });
            });
            api.groups = groups;
            api.models = models;
        },
        //
        // Create the form for adding a data grid
        _get_form: function (api) {
            var form = lux.web.form(),
                select_model = form.add_input('select', {name: 'url'}),
                models = api.models;

            select_model.append($(document.createElement('option')).html('Choose a model'));
            _(api.groups).forEach(function (group) {
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
    });
