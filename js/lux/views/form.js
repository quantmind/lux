    //  Form view
    //  -----------------
    //
    //  Javascript view for forms and form fields
    var
    //
    globalAttributes = ['title'],
    //
    noControlClass = ['checkbox', 'radio'],
    //
    controlClass = 'form-control',
    //
    Form = lux.Form = lux.createView('form', {
        //
        selector: 'form[data-lux]',
        //
        tagName: 'form',
        //
        defaults: {
            dataType: "json",
            layout: null,
            ajax: false,
            complete: null,
            error: null,
            validate: false,
            success: lux.ajaxResponse
        },
        //
        initialise: function (options) {
            var elem = this.elem;
            if (elem.hasClass('horizontal')) {
                options.layout = 'horizontal';
            } else if (elem.hasClass('inline')) {
                options.layout = 'inline';
            }
            if (options.layout) {
                this.layout = options.layout;
                elem.addClass('form-' + this.layout);
            }
            if (options.ajax || elem.hasClass('ajax')) {
                this.ajax(options);
            }
            // Check if we need to use parsleyjs for form validation
            if (options.validate !== false) {
                options.validate = true;
                require(['parsley'], function () {
                    elem.attr('novalidate','novalidate').parsley({
                        successClass: 'success',
                        errorClass: 'error',
                        classHandler: function(el) {
                            return $(el).closest('.control-group');
                        },
                        errorsWrapper: '<span class=\"help-inline\"></span>',
                        errorElem: '<span></span>'
                    });
                });
            }
        },
        //
        // Apply the ``jquery-form`` ajax plugin to this form
        ajax: function (options) {
            var elem = this.elem;
            require(['jquery-form'], function () {
                elem.ajaxForm(options);
            });
        },
        //
        // Add a list of ``Fields`` to this form.
        addFields: function (fields, options) {
            var processed = [],
                self = this,
                elem,
                fieldset;
            //
            _(fields).forEach(function (field) {
                if (field && field.name && processed.indexOf(field.name) === -1) {
                    processed.push(field.name);
                    field.render(self, options);
                }
            });
            return this;
        },
        //
        // Add a submit button
        addSubmit: function (options) {
            options || (options = {});
            if (!options.tagName) {
                options.tagName = 'button';
                if (!options.text) options.text = 'Submit';
            }
            var btn = new Button(options);
            this.fieldset(options.fieldset).append(btn.elem);
            return btn;
        },
        //
        render: function () {
            if (this.layout) {
                var layout = this['render_' + this.layout];
                layout.call(this);
            } else {
                var self = this;
                $('input,select,textarea', this.elem).each(function () {
                    var elem = $(this);
                    if (noControlClass.indexOf(elem.attr('type')) === -1)
                        elem.addClass(controlClass);
                });
            }
            return this;
        },
        //
        render_inline: function () {
            var self = this;
            $('input,select', this.elem).each(function () {
                var elem = $(this);
                if (noControlClass.indexOf(elem.attr('type')) === -1) {
                    elem.parent().find('label').addClass('sr-only');
                    elem.addClass(controlClass);
                }
            });
        },
        //
        render_horizontal: function () {
            var self = this,
                elem, label, parent, wrap, group;
            $('input,select', this.elem).each(function () {
                elem = $(this).addClass(controlClass);
                wrap = elem.closest(self.groupClass);
                if (wrap.length) {
                    parent = elem.parent();
                    if (!parent.is('label')) parent = elem;
                    wrap = $(document.createElement('div')).addClass('controls');
                    parent.before(wrap).appendTo(wrap);
                    group = wrap.parent();
                    if (!wrap.hasClass('control-group')) {
                        label = wrap.prev();
                        group = $(document.createElement('div')).addClass('control-group');
                        wrap.before(group).appendTo(group);
                        if (label.is('label')) {
                            group.prepend(label.addClass('control-label'));
                        }
                    }
                }
            });
        },
        //
        //  Get a fieldset from the form if possible
        //
        //  If ``fieldset_selector`` is not specified or a fieldset is not found
        //  return the form element.
        fieldset: function (fieldset_selector) {
            if (!fieldset_selector) {
                return this.elem;
            } else if (fieldset_selector instanceof jQuery) {
                return fieldset_selector;
            } else if (fieldset_selector instanceof HTMLElement) {
                return $(fieldset_selector);
            } else {
                var elem = this.elem.find(fieldset_selector);
                if (!elem.length) elem = this.elem.find('.'+fieldset_selector);
                return elem.length ? elem : this.elem;
            }
        }
    }),
    //
    //  Base class for ``Form`` fields
    //
    //  * ``label``, if set to ``false`` no label is displaied
    Field = lux.Field = lux.Class.extend({
        fieldOptions: [
            'tagName', 'type', 'label', 'placeholder', 'fieldset'],
        //
        attributes: _.union([
            'accept', 'alt', 'autocomplete', 'autofocus', 'disabled',
            'form', 'formaction', 'readonly', 'required'], globalAttributes),
        //
        formGroup: 'form-group',
        //
        tagName: 'input',
        //
        type: 'text',
        //
        init: function (name, options) {
            options || (options = {});
            this.name = name;
            _.extend(this, _.pick(options, this.fieldOptions));
            this.attributes = _.pick(options, this.attributes);
            if (!this.attributes.title) this.attributes.title = this.name;
            if (this.label !== false)
                this.label = this.getLabel();
            if (this.required) this.required = 'required';
        },
        //
        validate: function (model, value) {
            if (value || value === 0) return value + '';
        },
        //
        setValue: function (model, elem) {
            if (model) elem.val(model.get(this.name));
        },
        //
        // Render this field for the ``form``.
        // Return a jQuery element which can be included in the ``form``.
        render: function (form, options) {
            var
            elem = $(document.createElement(this.tagName)).attr(
                this.attributes),
            placeholder = this.getPlaceholder();
            elem.attr('name', this.name);
            if (this.tagName === 'input')
                elem.attr('type', this.type);
            var type = elem.attr('type');
            if (noControlClass.indexOf(type) === -1)
                elem.addClass(controlClass);
            //
            if (placeholder)
                elem.attr('placeholder', placeholder);
            if (_.isFunction(form)) form(elem);
            else {
                this.setValue(form.model, elem);
                if (type !== 'hidden')
                    elem = this.outerContainer(elem, form);
                form.fieldset(this.fieldset).append(elem);
            }
        },
        //
        getPlaceholder: function () {
            if (this.placeholder !== false)
                return this.placeholder ? this.placeholder : this.getLabel();
        },
        //
        getLabel: function () {
            return this.label || lux.niceStr(this.name);
        },
        //
        // Wrap field and label with an outer container
        outerContainer: function (elem, form) {
            var outer = $(document.createElement('div')).addClass(this.formGroup);
            if (this.label) {
                var id = elem.attr('id');
                if (!id) {
                    id = _.uniqueId('field');
                    elem.attr('id', id);
                }
                //
                $(document.createElement('label')).html(this.label
                    ).attr('for', id).appendTo(outer);
            }
            return outer.append(elem);
        }
    }),
    //
    IntegerField = lux.Field = Field.extend({
        type: 'number',
        //
        validate: function (model, value) {
            return parseInt(value, 10);
        }
    }),
    //
    FloatField = lux.FloatField = Field.extend({
        type: 'number',
        //
        validate: function (model, value) {
            return parseFloat(value);
        }
    }),
    //
    BooleanField = lux.BooleanField = Field.extend({
        type: 'checkbox',
        //
        controlClass: null,
        //
        setValue: function (model, elem) {
            if (model) {
                var val = model.get(this.name) ? true : false;
                elem.prop('checked', val);
            }
        },
        //
        validate: function (model, value) {
            if (value !== undefined)
                return value === true || value === 'on';
        },
        //
        outerContainer: function (elem, form) {
            var label = $(document.createElement('label')),
                outer = $(document.createElement('div')).addClass('checkbox');
            elem = outer.append(label.append(elem).append(this.label));
            form.fieldset(this.fieldset).append(elem);
            return elem;
        },
    }),
    //
    // A ``ChoiceField`` is by default rendered as a ``select`` element.
    //
    //  A ``select2`` object or function can be passed during construction.
    //  In this case the ``select2`` jQuery plugin is applied.
    ChoiceField = lux.ChoiceField = Field.extend({
        //
        // If the ``select`` dictionary is passed and the ``tagName`` is ``select``
        // the jQuery select plugin is applied.
        fieldOptions: _.union(
            Field.prototype.fieldOptions,
            ['choices', 'select2']),
        //
        tagName: 'select',
        //
        type: null,
        //
        setValue: function (model, elem) {
            if (model) {
                var val = model.get(this.name);
                if (elem.is('select')) {
                } else if (elem.val() === val) {
                    elem.prop('checked', true);
                }
            }
        },
        //
        //  Render this ``ChoiceField`` into ``form``
        //
        //  ``form`` can be a ``Form`` instance or a function accepting the
        //  new jQuery element created
        render: function (form) {
            var self = this,
                choices= this.choices,
                elem, text;
            if (_.isFunction(choices)) choices = choices(form);
            //
            // Select element
            if (this.tagName === 'select') {
                elem = $(document.createElement(this.tagName)).attr({
                    name: this.name
                }).append($("<option></option>")).addClass(controlClass);
                //
                _(choices).forEach(function (val) {
                    if (!(val instanceof jQuery)) {
                        if (_.isString(val)) text = val;
                        else {
                            text = val.text || val.value;
                            val = val.value;
                        }
                        val = $("<option></option>").val(val).text(text);
                    }
                    elem.append(val);
                });
                if (_.isFunction(form)) form(elem);
                else {
                    self.setValue(form.model, elem);
                    form.fieldset(this.fieldset).append(
                        self.outerContainer(elem, form));
                }
                var opts = this.select2;
                if (_.isFunction(opts)) opts = opts(form);
                if (opts) {
                    if (!opts.placeholder) opts.placeholder = this.getPlaceholder();
                    elem.Select(opts);
                }
                return elem;
            //
            // Radio element
            } else if (this.tagName === 'input' && this.type === 'radio') {
                _(choices).forEach(function (val) {
                    if (val instanceof string) text = val;
                    else {
                        text = val.text || val.value;
                        val = val.value;
                    }
                    elem = $(document.createElement(this.tagName)).attr({
                        type: 'radio',
                        name: self.name,
                        value: val
                    }).html(text);
                    self.setValue(form.model, elem);
                });
                form.elem.append(elem);
            }
        }
    }),
    //
    MultiField = lux.MultiField = ChoiceField.extend({

        render: function (form) {
            if (this.tagName === 'select') {
                var elem = this._super(form);
                return elem;
            }
        }
    }),
    //
    TextArea = lux.TextArea = Field.extend({
        tagName: 'textarea',
        //
        formGroup: 'textarea',
        //
        attributes: _.union(
            Field.prototype.attributes,
            ['rows', 'cols'])
    }),
    //
    KeywordsField = lux.KeywordsField = Field.extend({
        //
        validate: function (instance, value) {
            if (_.isString(value)) {
                var result = [];
                _(value.split(',')).forEach(function (el) {
                    el = el.trim();
                    if (el) {
                        result.push(el);
                    }
                });
                return result;
            } else if (!_.isArray(value)) {
                var val = [];
                _(value).forEach(function (v) {
                    val.push(v);
                });
                return val;
            } else {
                return value;
            }
        }
    });
    //
    //
    //  Select2 utilities
    //  ------------------------
    //
    //  A proxy for select2
    $.fn.Select = function (options) {
        options || (options = {});
        var self = this;
        require(['select'], function () {
            //if (_.isObject(options)) options.width = 'element';
            self.select2(options);
        });
        return this;
    };

    //
    // Select2 hook for lux set_value_hooks
    var get_select2_value = function (element, value) {
        if (element.hasClass('select2-offscreen')) {
            element.select2('val', value);
            return true;
        }
    };
    //
    lux.set_value_hooks.push(get_select2_value);
