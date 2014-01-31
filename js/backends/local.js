    // Local Storage backend
    var Storage = lux.Storage = Backend.extend({
        options: {
            type: 'local' // or session
        },
        //
        init: function (options, handlers) {
            this._super(null, options);
            if (this.options.type === 'local') {
                this.storage = localStorage;
            } else if (this.options.type === 'session') {
                this.storage = sessionStorage;
            } else {
                throw new lux.NotImplementedError('unknown storage ' + this.options.type);
            }
        },
        //
        // this.send({resource: 'status', success: function (){...}});
        send: function (options) {
            var s = this.submit_options(options);
            if (s.beforeSend && s.beforeSend.call(s, this) === false) {
                // Don't send anything, simply return
                return;
            }
            var handler,
                action = s.action || CrudMethod[s.type] || s.type;
            if (action) {
                handler = this[action.toLowerCase().replace('-','_')];
            }
            if (handler) {
                var self = this;
                handler.call(this, s.data, s.model, function (response) {
                    response.action = action;
                    if (response.error && s.error) {
                        s.error(response.error, self, response);
                    } else if (s.success && !response.error) {
                        s.success(response.data, self, response);
                    }
                });
            } else {
                if (s.error) {
                    var response = {
                            error: 'Unknown "' + action + '" action.',
                            'action': action
                        };
                    s.error(response.error, this, response);
                }
            }
        },
        //
        ping: function (data, model, callback) {
            callback({'data': 'pong'});
        },
        //
        post: function (models, model, callback) {
            var storage = this.storage;
            $.each(models, function () {
                var avail = true, id, key;
                while (avail) {
                    id = lux.s4();
                    key = model + '.' + id;
                    avail = storage.getItem(key);
                }
                this.fields.id = id;
                storage.setItem(key, JSON.stringify(this.fields));
            });
            callback({data: models});
        },
        //
        get: function (ids, model, callback) {
            var storage = this.storage,
                data = [];
            $.each(ids, function () {
                var key = model + '.' + this,
                    item = storage.getItem(key);
                if (item) {
                    data.push({id: this, fields: JSON.parse(item)});
                }
            });
            callback({'data': data});
        },
        //
        put: function (models, model, callback) {
            var storage = this.storage;
            $.each(models, function () {
                var key = model + '.' + this.id;
                storage.setItem(key, JSON.stringify(this.fields));
            });
            callback({data: models});
        },
        //
        // Delete models with primary keys in pks.
        destroy: function (ids, model, callback) {
            var storage = this.storage;
            $.each(ids, function () {
                storage.removeItem(model + '.' + this);
            });
            callback({'data': ids});
        }
    });