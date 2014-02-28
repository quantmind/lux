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
    cms.create_content_type('contenturl', {
        meta: {
            title: 'Site Content',
            fields: [
                new lux.ChoiceField('content_url', {
                    label: 'Choose a content',
                    choices: function () {
                        var vals = [];
                        _(lux.content_urls).forEach(function (value) {
                            vals.push(value);
                        });
                        return vals;
                    }
                })
            ]
        },
        //
        render: function (container, skin) {
            var url = this.get('content_url');
            if (url === 'this') {
                // defer to later
                var html = this.get('this');
                _.defer(function () {
                    lux.loadViews(container.html(html));
                });
            } else if (url) {
                container.html('&nbsp;');
                $.ajax(url, {
                    dataType: 'json',
                    success: function (data, status, xhr) {
                        if (data.html) {
                            require(data.requires || [], function () {
                                lux.loadViews(container.html(data.html));
                            });
                        }
                    }
                });
            } else {
                logger.warning('Missing underlying page url and html');
            }
        }
    });
    //
    //  Blank Content
    //  -------------------
    //
    //  Insert a non-breaking space.
    cms.create_content_type('blank', {
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
    cms.create_content_type('markdown', {
        //
        meta: {
            title: 'Text using markdown',
            persistent: true,
            fields: [
                new lux.TextArea('raw', {
                    rows: 10,
                    placeholder: 'Write markdown'
                }),
                new lux.TextArea('javascript', {
                    rows: 7,
                    placeholder: 'javascript'
                })
            ]
        },
        //
        render: function (container) {
            var self = this;
            require(['showdown'], function () {
                var raw = self.get('raw') || '',
                    js = self.get('javascript') || '',
                    converter = new Showdown.converter(),
                    html = converter.makeHtml(raw);
                lux.loadViews(container.html(html));
                if (js) {
                    var b = $('body'),
                        script = $("<script type='application/javascript'>" + js + "</script>"),
                        cid = self.cid();
                    $('#' + cid, b).remove();
                    b.append(script.attr('id', cid));
                }
            });
        },
        //
        get_form_new: function (callback) {
            var f = this._meta.fields,
                form = lux.web.form(),
                raw = f.raw.add_to_form(form, this),
                js = f.javascript.add_to_form(form, this),
                tabs = new lux.TabView({tabs: [
                    {
                        name: 'markdown',
                        content: raw
                    },
                    {
                        name: 'javascript',
                        content: js
                    }]
                });
            form._element.empty().append(tabs.elem);
            require(['codemirror'], function () {
                CodeMirror.fromTextArea(raw[0]);
                CodeMirror.fromTextArea(js[0]);
                callback(form);
            });
        }
    });
    //
    //  Versions
    //  -------------------
    cms.create_content_type('versions', {
        meta: {
            title: 'Versions of libraries'
        },
        //
        render: function (container) {
            var ul = $(document.createElement('ul')).appendTo(container);
            _(lux.libraries).forEach(function (lib) {
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
            //
            persistent: true,
            //
            render_queue: [],
            //
            api_info: function (api) {
                this.api = api || {};
                var queue = this.render_queue;
                delete this.render_queue;
                _.each(queue, function (o) {
                    o.content._render(o.container, o.skin);
                });
            },
            //
            fields: [
                new lux.ChoiceField('url', {
                    label: 'Choose a model',
                    choices: function (form) {
                        var api = form.model.api();
                        return api.groups;
                    },
                    select2: {}
                }),
                new lux.MultiField('fields', {
                    placeholder: 'Select fields to display',
                    select2: {}
                }),
                new lux.MultiField('row_actions', {
                    label: 'Row actions',
                    placeholder: 'Action on rows',
                    choices: [{value: 'delete'}],
                    select2: {
                        minimumResultsForSearch: -1
                    }
                }),
                new lux.ChoiceField('style', {
                    tag: 'input',
                    choices: ['table', 'grid']
                }),
                new lux.BooleanField('sortable'),
                new lux.BooleanField('editable'),
                new lux.BooleanField('collapsable'),
                new lux.BooleanField('fullscreen'),
                new lux.BooleanField('footer', {
                    label: 'Display Footer'
                })
            ]
        },
        //
        render: function (container, skin) {
            var self = this;
            require(['datagrid'], function () {
                if (self._meta.api === undefined) {
                    self._meta.render_queue.push({
                        content: self,
                        'container': container,
                        'skin': skin
                    });
                } else {
                    self._render(container, skin);
                }
            });
        },
        //
        getForm: function () {
            var form = this._super();
            this._formActions(form);
            return form;
        },
        //
        // Internal methods

        //
        // Actually does the datagrid rendering
        _render: function (container, skin) {
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
                options.store = options.url;
                options.skin = skin;
                elem.datagrid(options);
            }
        },
        //
        api: function () {
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
                var group = $(document.createElement('optgroup')).attr(
                    'label', section.name);
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
        // Add action to the datagrid form
        _formActions: function (form) {
            var self = this,
                api = this.api(),
                models = api.models,
                fields_select = form.elem.find('[name="fields"]');
            //
            // When a model change, change the selction as well.
            form.elem.find('[name="url"]').change(function (e) {
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
            }).val(this.get('url')).trigger('change');
        },
    });
