    //
    var CrudMethod = lux.CrudMethod = {
            create: 'POST',
            read: 'GET',
            update: 'PUT',
            destroy: 'DELETE'
        };
    //
    // Base class for backends to use when synchronising Models
    //
    // Usage::
    //
    //      backend = lux.Socket('ws://...')
    lux.Backend = lux.EventClass.extend({
        //
        options: {
            submit: {
                dataType: 'json'
            }
        },
        //
        init: function (url, options, type) {
            this.type = type;
            this.url = url;
            this.options = _.merge({}, this.options, options);
            this.submit = this.options.submit || {};
        },
        //
        // The synchoronisation method for models
        // Submit a bunch of data related to an instance of a model or a
        // group of model instances
        send: function (options) {},
        //
        submit_options: function (options) {
            if (options !== Object(options)) {
                throw new TypeError('Send method requires an object as input');
            }
            return _.extend({}, this.submit, options);
        },
        //
        toString: function () {
            return this.type + ' ' + this.url;
        }
    });