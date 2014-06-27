    //
    // Web Broweser Local Storage backend
    var Storage = lux.Backend.extend({
        //
        init: function (url, options, type) {
            this._super(url, options, type);
            var idx = this.url.search('://');
            this.namespace = this.url.substr(idx+3);
            if (this.type === 'local') {
                this.storage = localStorage;
            } else if (this.type === 'session') {
                this.storage = sessionStorage;
            } else {
                throw new lux.NotImplementedError('unknown storage ' + this.type);
            }
        },
        //
        // this.send({resource: 'status', success: function (){...}});
        execute: function (options) {
            if (options.beforeSend && options.beforeSend.call(options, this) === false) {
                // Don't send anything, simply return
                return;
            }
            //
            // This is an execution for a single item
            if (options.item) {
                options.data = [options.item];
            }
            var action = options.crud,
                storage = this.storage,
                prefix = this.namespace;
            //
            if (action === Crud.create) {
                _(options.data).forEach(function (obj) {
                    storage.setItem(prefix + obj.cid, JSON.stringify(obj.fields));
                });
            } else if (action === Crud.update) {
                _(options.data).forEach(function (obj) {
                    var fields = storage.getItem(prefix + obj.cid);
                    if (fields) {
                        fields = _.extend(SON.parse(fields), obj.fields);
                        storage.setItem(prefix + obj.cid, JSON.stringify(fields));
                    }
                });
            } else if (action === Crud.delete) {
                _(options.data).forEach(function (obj) {
                    storage.removeItem(prefix + obj.cid);
                });
            }
        }
    });

    lux.register_store('local', Storage);
    lux.register_store('session', Storage);
    //