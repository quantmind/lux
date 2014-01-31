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
                element = this.element(),
                fieldset = element.children('fieldset'),
                // textarea and button dont have value attribute, use as text
                value = input.value;
            delete input.label;

            if (!fieldset.length) {
                if (!element.children().length) {
                    fieldset = $(document.createElement('fieldset')).appendTo(element);
                } else {
                    fieldset = element;
                }
            }

            switch (type) {
            case 'textarea':
                elem = $(document.createElement('textarea')).attr(input).html(value);
                break;
            case 'submit':
                elem = this.submit(input);
                break;
            case 'select':
                elem = this.select(input);
                break;
            default:
                elem = this.input(input);
            }
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
        // A special case of ``add_input``, add a select
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