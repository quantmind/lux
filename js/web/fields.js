    //
    // Fields for Forms and Models

    var c = lux;

    c.Field = lux.Class.extend({
        tag: 'input',
        type: 'text',
        //
        init: function (options) {
            this.options = Object(options);
        },
        //
        validate: function (model, value) {
            if (value || value === 0) return value + '';
        },
        //
        set_value: function (model, elem) {
            elem.val(model.get(this.name));
        },
        //
        add_to_form: function (form, model) {
            var opts = _.extend({
                name: this.name,
                type: this.type,
                title: this.name
            }, this.options);
            var elem = form.add_input(this.tag, opts);
            if (model) {
                this.set_value(model, elem);
            }
            return elem;
        }
    });

    c.IntegerField = c.Field.extend({
        type: 'number',
        //
        validate: function (model, value) {
            return parseInt(value, 10);
        }
    });

    c.FloatField = c.Field.extend({
        type: 'number',
        //
        validate: function (model, value) {
            return parseFloat(value);
        }
    });

    c.BooleanField = c.Field.extend({
        type: 'checkbox',
        //
        set_value: function (model, elem) {
            if (model.get(this.name)) {
                elem.prop('checked', true);
            }
        },
        //
        validate: function (model, value) {
            if (value !== undefined)
                return value === true || value === 'on';
        }
    });

    c.MultiField = c.Field.extend({
        tag: 'select',
        //
        init: function (options) {
            this.options = Object(options);
            this.options.multiple = 'multiple';
        }
    });

    c.TextArea = c.Field.extend({
        tag: 'textarea'
    });

    c.KeywordsField = c.Field.extend({

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
