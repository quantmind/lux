    //
    // jQuery Form
    var special_inputs = ['checkbox', 'radio'],
        jquery_form_info = function () {
            return {name: 'jquery-form',
                    version: '3.48',
                    web: 'http://malsup.com/jquery/form/'};
        };
    //
    web.extension('form', {
        selector: 'form',
        defaultElement: 'form',
        //
        options: {
            dataType: "json",
            layout: 'default',
            ajax: false,
            complete: null,
            error: null,
            success: null
        },
        //
        decorate: function () {
            var form = this,
                element = form.element();
            if (element.hasClass('ajax')) {
                form.options.ajax = true;
            }
            if (element.hasClass('horizontal')) {
                this.options.layout = 'horizontal';
            } else if (element.hasClass('inline')) {
                this.options.layout = 'inline';
            }
            var layout = this['render_' + this.options.layout];
            if (layout) layout.call(this);
            if (form.options.ajax) {
                form.options.ajax = false;
                form.ajax();
            }
        },
        //
        render_horizontal: function () {
            var elem, label, parent, wrap, group;
            $('input,select,textarea,button', this.element().addClass('horizontal')).each(function () {
                elem = $(this);
                wrap = elem.parent();
                if (!wrap.hasClass('controls')) {
                    parent = elem.parent();
                    if (!parent.is('label')) parent = elem;
                    wrap = $(document.createElement('div')).addClass('controls');
                    parent.before(wrap).appendTo(wrap);
                }
                group = wrap.parent();
                if (!wrap.hasClass('control-group')) {
                    label = wrap.prev();
                    group = $(document.createElement('div')).addClass('control-group');
                    wrap.before(group).appendTo(group);
                    if (label.is('label')) {
                        group.prepend(label.addClass('control-label'));
                    }
                }
            });
        },
        //
        render_inline: function () {
            var elem;
            $('input,select,button', this.element().addClass('inline')).each(function () {
                elem = $(this);
                if (special_inputs.indexOf(elem.attr('type')) === -1) {
                    elem.addClass('input-small');
                }
            });
        },
        //
        ajax: function (options) {
            if (!this.options.ajax) {
                if (options) {
                    $.extend(this.options, options);
                }
                var self = this;
                web.add_lib(jquery_form_info());
                options = self.options;
                options.ajax = true;
                options.error = options.error || self.on_error,
                options.success = options.success || self.on_success;
                this.element().ajaxForm(options);
            }
        },
        //
        // Add a new input to the form
        add_input: function (type, input) {
            input = input || {};
            var elem,
                label = input.label,
                element = this._element,
                fieldsets = element.children('fieldset'),
                fieldset_selector = input.fieldset,
                // textarea and button don't have value attribute,
                // therefore the value is used as text
                value = input.value,
                fieldset, fs;
            delete input.label;

            // Find the appropiate fieldset
            if (fieldset_selector) {
                if (fieldset_selector.id) {
                    fs = fieldsets.find('#' + fieldset_selector.id);
                } else if (fieldset_selector.Class) {
                    fs = fieldsets.find('.' + fieldset_selector.Class);
                } else {
                    fs = fieldsets.first();
                }
                if (fs.length) {
                    fieldset = fs;
                } else {
                    fieldset = $(document.createElement('fieldset')).appendTo(element);
                    if (fieldset_selector.id) {
                        fieldset.attr(id, fieldset_selector.id);
                    } else if (fieldset_selector.Class) {
                        fieldset.addClass(fieldset_selector.Class);
                    }
                }
            } else if (!fieldsets.length) {
                if (!element.children().length) {
                    fieldset = $(document.createElement('fieldset')).appendTo(element);
                } else {
                    fieldset = element;
                }
            } else {
                fieldset = fieldsets.first();
            }
            if (type === 'textarea') {
                elem = $(document.createElement('textarea')).attr(input).html(value);
            } else if (type === 'submit') {
                elem = this.submit(input);
            } else if (type === 'select') {
                elem = this.select(input);
            } else if (_.isString(type)) {
                elem = this.input(input);
            } else {
                elem = type;
            }
            //
            if (label) {
                label = $(document.createElement('label')).html(label);
            }
            if (special_inputs.indexOf(elem.attr('type')) > -1) {
                if (!label) {
                    label = $(document.createElement('label'));
                }
                fieldset.append(label.addClass('checkbox').append(elem));
            } else {
                fieldset.append(label);
                fieldset.append(elem);
            }
            return elem;
        },
        //
        input: function (options) {
            if (!options) options = {};
            if(!options.type) options.type='text';
            return $(document.createElement('input')).attr(options);
        },
        //
        submit: function (options) {
            if (!options) options = {};
            if (!options.tag) {
                options.tag = 'button';
                options.text = options.value;
            }
            return web.create_button(options);
        },
        //
        // A special case of ``add_input``, add a select element
        select: function (options) {
            var value, elem;
            if (options) {
                delete options.type;
                value = options.value;
                delete options.value;
            }
            elem = $(document.createElement('select')).attr(options);
            return elem;
        },
        //
        on_error: function (o, s, xhr, form) {
            // Got a 400 Bad Request, the form did not validate
            if (o.status === 400) {

            }
        },
        //
        on_success: function (o, s, xhr, form) {
            // Got a 200 response
            if (o.redirect) {
                window.location = o.redirect;
            } else {
                _(o).forEach(function (messages, name) {
                    _(messages).forEach(function (message) {
                        if (message.error) {
                            message.skin = 'error';
                        } else {
                            message.skin = 'success';
                        }
                        var alert = web.alert(message),
                            field;
                        if (name) {
                            field = form.find('input[name='+name+']');
                        }
                        if (field.length) {
                            field.before(alert.element());
                        } else if (name === 'form') {
                            form.prepend(alert.element());
                        } else {
                            var container = $('.messages');
                            if (!container.length) {
                                form.prepend(alert.element());
                            } else {
                                container.append(alert.element());
                            }
                        }
                    });
                });
            }
        }
    });
