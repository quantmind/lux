    //
    var CrudMethod = {
            create: 'POST',
            read: 'GET',
            update: 'PUT',
            destroy: 'DELETE'
        };
    //
    var Backend = lux.Backend = lux.EventClass.extend({
        //
        options: {
            submit: {
                dataType: 'json'
            }
        },
        //
        init: function (url, options, type) {
            this.type = type || 'ajax';
            this.url = url;
            this.options = $.extend(true, {}, this.options, options || {});
            this.submit = this.options.submit || {};
        },
        //
        // The sync method for models
        send: function (options) {
            var s = this.submit_options(options);
            var url = this.url,
                data = s.data,
                model = s.model,
                action = s.action;
            s.type = CrudMethod[s.type] || s.type || 'GET';    
            if (model && data && data.length === 1) {
                if (s.type !== CrudMethod.create) {
                    url = lux.utils.urljoin(url, data[0].id);
                }
                s.data = data[0].fields;
                $.ajax(url, s);
            } else {
                $.ajax(url, s);
            }
        },
        //
        submit_options: function (options) {
            var s = options;
            if (s !== Object(s)) {
                throw new TypeError('Send method requires an object as input');
            }
            return $.extend({}, this.submit, s);
        },
        //
        toString: function () {
            return this.type + ' ' + this.url;
        }
    });
