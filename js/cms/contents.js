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
            persistent: true,
            fields: {
                raw: new lux.TextArea({
                    rows: 15,
                    placeholder: 'Write markdown'
                }),
                javascript: new lux.TextArea({
                    rows: 10,
                    placeholder: 'javascript'
                })
            }
        },
        //
        render: function (container) {
            var self = this;
            require(['showdown'], function () {
                var raw = self.get('raw') || '',
                    js = self.get('javascript') || '',
                    converter = new Showdown.converter(),
                    html = converter.makeHtml(raw);
                web.refresh(container.html(html));
                if (js) {
                    var b = $('body'),
                        script = $("<script type='application/javascript'>" + js + "</script>"),
                        sid = 'markdown-'+self.id();
                    $('#' + sid, b).remove();
                    b.append(script.attr('id', sid));
                }
            });
        },
        //
        get_form: function () {
            var f = this._meta.fields,
                form = lux.web.form();
            f.raw.add_to_form(form, this);
            f.javascript.add_to_form(form, this);
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
            },
            fields: {
                sortable: new lux.BooleanField({label: 'Sortable'}),
                editable: new lux.BooleanField({label: 'Editable'}),
                footer: new lux.BooleanField({label: 'Display Footer'}),
                row_actions: new lux.MultiField({
                    label: 'Row actions',
                    placeholder: 'Action on rows',
                    options: [{value: 'delete'}]
                })
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
        get_form: function () {
            // The select model is not yet available, create it.
            var api = this._api();
            if (api.groups) {
                return this._get_form(api);
            }
        },
        //
        // Internal methods

        //
        // Actually does the datagrid rendering
        _render: function (container) {
            var elem = $(document.createElement('div')).appendTo(container),
                options = _.extend({}, this.fields()),
                models = this._api().models,
                model = models ? models[options.url] : null,
                headers = [];
            if (model) {
                if (options.fields) {
                    var available_fields = {};
                    _(model.fields).forEach(function (elem) {
                        available_fields[elem.code] = elem;
                    });
                    _(options.fields).forEach(function (code) {
                        var head = available_fields[code];
                        if (head) {
                            headers.push(head);
                        }
                    });
                }
                if (headers.length) {
                    options.columns = headers;
                } else {
                    options.columns = model.fields;
                }
                options.ajaxUrl = options.url;
                lux.web.datagrid(elem, options);
            }
        },
        //
        _api: function () {
            var api = this._meta.api;
            if (api) {
                if (!api.groups && api.sitemap) {
                    this._create_groups(api);
                }
                return api;
            } else {
                return {};
            }
        },
        //
        // sitemap is a list of api section handlers
        _create_groups: function (api) {
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
            var self = this,
                form = lux.web.form(),
                select_model = form.add_input('select', {name: 'url'}),
                models = api.models,
                fields = this._meta.fields;

            select_model.append($(document.createElement('option')).html('Choose a model'));
            _(api.groups).forEach(function (group) {
                select_model.append(group);
            });
            // Create the fields multiple select
            var fields_select = form.add_input('select', {
                multiple: 'multiple',
                name: 'fields',
                placeholder: 'Select fields to display'
            }).select();
            //
            fields.sortable.add_to_form(form, this);
            fields.editable.add_to_form(form, this);
            fields.footer.add_to_form(form, this);
            fields.row_actions.add_to_form(form, this).select();
            //
            // When a model change, change the selction as well.
            select_model.select().change(function (e) {
                var url = $(this).val(),
                    model = models[url];
                // there is a model
                fields_select.val([]).trigger("change");
                fields_select.children().remove();
                if (model) {
                    //
                    // Add options
                    if (model.options) {
                        _(model.options).forEach(function (option) {
                            fields_select.append(option);
                        });
                    } else {
                        model.options = [];
                        model.map = {};
                        _(models[url].fields).forEach(function (field) {
                            var option = $(document.createElement('option'))
                                            .val(field.code).html(field.name);
                            model.map[field.code] = field;
                            model.options.push(option);
                            fields_select.append(option);
                        });
                    }
                    //
                    // The model correspoend with the current content model
                    // selct fields accordignly
                    if (url === self.get('url')) {
                        _(self.get('fields')).forEach(function (field) {

                        });
                    }
                }
            });
            //
            // If the model url is available trigger the changes in the select
            // element
            select_model.val(this.get('url')).trigger('change');
            return form;
        },
    });
