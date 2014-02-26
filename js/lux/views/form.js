
    var
    //
    // Form view
    Form = lux.Form = lux.createView('form', {
        //
        tagName: 'form',
        //
        defaults: {
            dataType: "json",
            layout: null,
            groupClass: 'form-group',
            controlClass: 'form-control',
            skin: 'default',
            ajax: false,
            complete: null,
            error: null,
            success: null
        },
        //
        initialise: function (options) {
            this.options = options;
            if (this.elem.hasClass('horizontal')) {
                options.layout = 'horizontal';
            } else if (this.elem.hasClass('inline')) {
                options.layout = 'inline';
            }
            if (options.layout)
                this.elem.addClass('form-' + options.layout);
            lux.setSkin(this.elem, options.skin);
        },
        //
        // Add a list of ``Fields`` to this form.
        addFields: function (fields) {
            var processed = [],
                self = this,
                elem,
                fieldset;
            //
            _(fields).forEach(function (field) {
                if (field && field.name && processed.indexOf(field.name) === -1) {
                    processed.push(field.name);
                    field.render(self);
                }
            });
            return this;
        },
        //
        // Add a submit button
        addSubmit: function (options) {
            options || (options = {});
            if (!options.skin) options.skin = this.options.skin;
            if (!options.tagName) {
                options.tagName = 'button';
                if (!options.text) options.text = 'Submit';
            }
            var btn = new Button(options);
            this.elem.append(btn.elem);
        },
        //
        render: function () {
            if (this.options.layout) {
                var layout = this['render_' + this.options.layout];
                layout.call(this);
            } else {
                var self = this;
                $('input,select,textarea', this.elem).each(function () {
                    var elem = $(this);
                    if (elem.attr('type') !== 'checkbox') {
                        elem.addClass(self.options.controlClass);
                    }
                });
            }
            return this;
        },
        //
        //
        render_horizontal: function () {
            var self = this,
                elem, label, parent, wrap, group;
            $('input,select,textarea', this.elem).each(function () {
                elem = $(this).addClass(self.options.controlClass);
                wrap = elem.closest(self.options.groupClass);
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
        fieldset: function (fieldset_selector) {
            var fieldsets = this.elem.children('fieldset'),
                fieldset;
            //
            // Find the appropiate fieldset
            if (fieldset_selector) {
                if (fieldset_selector instanceof jQuery) {
                    fs = fieldset_selector;
                } else if (fieldset_selector instanceof HTMLElement) {
                    fs = $(fieldset_selector);
                } else if (fieldset_selector.id) {
                    fs = this.elem.find('#' + fieldset_selector.id);
                } else if (fieldset_selector.Class) {
                    fs = this.elem.find('.' + fieldset_selector.Class);
                } else {
                    fs = fieldsets.last();
                }
                if (fs.length) {
                    fieldset = fs;
                } else {
                    fieldset = $(document.createElement('fieldset')).appendTo(this.elem);
                    if (fieldset_selector.id) {
                        fieldset.attr(id, fieldset_selector.id);
                    } else if (fieldset_selector.Class) {
                        fieldset.addClass(fieldset_selector.Class);
                    }
                }
            } else if (!fieldsets.length) {
                fieldset = $(document.createElement('fieldset')).appendTo(this.elem);
            } else {
                fieldset = fieldsets.first();
            }
            return fieldset;
        }
    }),
    //
    //  Base class for ``Form`` fields
    Field = lux.Field = lux.Class.extend({
        fieldOptions: [
            'tagName', 'type', 'label', 'placeholder', 'autocomplete',
            'required', 'fieldset'],
        //
        tagName: 'input',
        //
        type: 'text',
        //
        init: function (name, options) {
            options || (options = {});
            this.name = name;
            _.extend(this, _.pick(options, this.fieldOptions));
            this.label = this.label || this.name.capitalize();
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
        render: function (form) {
            var
            elem = $(document.createElement(this.tagName)).attr({
                name: this.name,
                type: this.type,
                title: this.title || this.name,
                autocomplete: this.autocomplete,
                placeholder: this.getPlaceholder()
            });
            this.setValue(form.model, elem);
            form.elem.append(this.outerContainer(elem, form));
        },
        //
        getPlaceholder: function () {
            if (this.placeholder !== false)
                return this.placeholder ? this.placeholder : this.label;
        },
        //
        // Wrap field and label with an outer container ``div.groupClass``.
        outerContainer: function (elem, form) {
            if (form.layout !== 'inline') {
                var id = elem.attr('id');
                if (!id) {
                    id = _.uniqueId('field');
                    elem.attr('id', id);
                }
                //
                var label = $(document.createElement('label')).html(this.label
                        ).attr('for', id),
                    outer = $(document.createElement('div')).addClass(
                        form.options.groupClass);
                return outer.append(label).append(elem);
            } else {
                return elem;
            }
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
        //
        render: function (form) {
            var elem = $(document.createElement(this.tagName)).attr({
                name: this.name,
                type: this.type,
                title: this.title
            });
            this.setValue(form.model, elem);
            var label = $(document.createElement('label')),
                outer = $(document.createElement('div')).addClass('checkbox');
            elem = outer.append(label.append(elem).append(this.label));
            form.elem.append(elem);
        },
    }),
    //
    // A ``ChoiceField`` is by default rendered as a ``select`` element.
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
        render: function (form) {
            var self = this,
                choices= this.choices,
                elem, text;
            if (_.isFunction(choices)) choices=  choices();
            //
            // Select element
            if (this.tagName === 'select') {
                elem = $(document.createElement(this.tagName)).attr({
                    name: this.name
                }).append($("<option></option>"));
                //
                _(choices).forEach(function (val) {
                    if (_.isString(val)) text = val;
                    else {
                        text = val.text || val.value;
                        val = val.value;
                    }
                    elem.append($("<option></option>").val(val).text(text));
                });
                self.setValue(form.model, elem);
                form.elem.append(self.outerContainer(elem, form));
                if (this.select2) {
                    var opts = this.select2;
                    if (!opts.placeholder) opts.placeholder = this.getPlaceholder();
                    elem.Select(opts);
                }
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
        //
        init: function (options) {
            this.options = Object(options);
            this.options.multiple = 'multiple';
        }
    }),
    //
    TextArea = lux.TextArea = Field.extend({
        tagName: 'textarea'
    }),
    //
    KeywordsField = lux.KeywordsField = Field.extend({

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
    // A proxy for select2
    $.fn.Select = function (options) {
        options || (options = {});
        var self = this;
        require(['select'], function () {
            if (_.isObject(options)) options.width = 'element';
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
