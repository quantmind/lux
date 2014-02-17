    //
    var
    // CRUD actions
    Crud = {
        create: 'create',
        read: 'read',
        update: 'update',
        'delete': 'delete',
    },
    CrudMethod = lux.CrudMethod = {
        create: 'POST',
        read: 'GET',
        update: 'PUT',
        destroy: 'DELETE'
    },
    //
    stores = {},
    //
    register_store = lux.register_store = function (scheme, Store) {
        stores[scheme] = Store;
    },
    //
    // Create a new Backend Store from a ``store`` url
    //
    create_store = lux.create_store = function (store, options) {
        if (store instanceof Backend) {
            return store;
        } else if (_.isString(store)) {
            var idx = store.search('://');
            if (idx > -1) {
                var scheme = store.substr(0, idx),
                    Store = stores[scheme];
                if (Store) {
                    return new Store(store, options, scheme);
                }
            }
        }
        // A dummy backend
        return new Backend(store, options, 'dummy');
    };
    //
    // Base class for backends to use when synchronising Models
    //
    // Usage::
    //
    //      backend = lux.Socket('ws://...')
    var Backend = lux.Backend = lux.Class.extend({
        //
        options: {
            dataType: 'json'
        },
        //
        init: function (url, options, type) {
            this.type = type;
            this.url = url;
            this.options = _.merge({}, this.options, options);
        },
        //
        // The synchoronisation method
        //
        // It has an API which match jQuery.ajax method
        //
        // Available options entries:
        // * ``beforeSend`` A pre-request callback function that can be used to
        //   modify the object before it is sent. Returning false will cancel the
        //   execution.
        // * ``error`` callback invoked if the execution fails
        // * ``meta`` optional Model metadata
        // * ``model`` optional Model instance
        // * ``success`` callback invoked on a successful execution
        // * ``type`` the type of CRUD operation
        execute: function (options) {
            if (options.success) {
                options.success([]);
            }
        },
        //
        toString: function () {
            return this.type + ' ' + this.url;
        }
    });

    //  AJAX Backend
    //  -------------------------
    //
    //  Uses jQuery.ajax method to execute CRUD operations
    var AjaxBackend = lux.Backend.extend({
        //
        init: function (url, options, type) {
            this._super(url, options, 'ajax');
        },
        //
        // The ajax execute method for single model or group of models
        execute: function (options) {
            var url = this.url,
                model = options.model,
                item = options.item;
            delete options.model;
            //
            options.type = lux.CrudMethod[options.crud] || options.type || 'GET';
            //
            // If a model is given, this is an operation on a single instance
            if (item) {
                delete options.item;
                // primary key given, change url
                if (item.pk) url = lux.utils.urljoin(url, item.pk);
                options.data = item.fields;
            }
            $.ajax(url, options);
        }
    });
    //
    register_store('http', AjaxBackend);
    register_store('https', AjaxBackend);

    //
    //  WebSocket Backend
    //  ----------------------------------------
    //
    //  Uses lux websocket CRUD protocol
    var Socket = lux.Backend.extend({
        //
        options: {
            resource: null,
            reconnecting: 1,
            hartbeat: 5,
            maxDelay: 3600,
            maxRetries: null,
            factor: 2.7182818284590451, // (e)
            jitters: 0,
            jitter: 0.11962656472
        },
        //
        init: function (url, options, type) {
            var self = this;
            url = this.websocket_uri(url);
            this._super(url, options, 'websocket');
            this._retries = 0;
            this._transport = null;
            this._opened = false;
            this._pending_messages = {};
            this._delay = this.options.reconnecting;
            this._queue = [];
            self.connect();
        },
        //
        opened: function () {
            return this._opened;
        },
        //
        // Connect the websocket
        // This method can be called several times by the
        // reconnect method (reconnecting must be positive).
        connect: function () {
            var options = this.options,
                uri = this.url,
                self = this;
            if (options.resource) {
                uri += options.resource;
            }
            logger.info('Connecting with ' + self);
            this._transport = new WebSocket(uri);
            this._transport.onopen = function (e) {
                self.onopen();
            };
            this._transport.onmessage = function (e) {
                if (e.type === 'message') {
                    self.onmessage(e);
                }
            };
            this._transport.onclose = function (e) {
                self.onclose();
            };
        },
        //
        onopen: function () {
            this._opened = true;
            logger.info(this + ' opened.');
            if (this.options.onopen) {
                this.options.onopen.call(this);
            }
            if (this._queue) {
                var queue = this._queue;
                this._queue = [];
                _(queue).forEach(function (msg) {
                    this._transport.send(msg);
                }, this);
            }
        },
        //
        reconnect: function () {
            var o = this.options,
                self = this;
            if (!this._delay) {
                web.logger.info('Exiting websocket');
                return;
            }
            this._retries += 1;
            if (o.maxRetries !== null && (this._retries > o.maxRetries)) {
                web.logger.info('Exiting websocket after ' + this.retries + ' retries.');
                return;
            }
            //
            this._delay = Math.min(this._delay * o.factor, o.maxDelay);
            if (o.jitter) {
                this._delay = lux.math.normalvariate(this._delay, this._delay * o.jitter);
            }
            //
            web.logger.info('Try to reconnect websocket in ' + this._delay + ' seconds');
            this.trigger('reconnecting', this._delay);
            this._reconnect = lux.eventloop.call_later(this._delay, function () {
                self._reconnect = null;
                self.connect();
            });
        },
        //
        // Send a set of operations to the backend
        // If ``options`` contains the ``item`` entry, than it is converted into
        // a sinle ``data`` entry ``options.data = [options.item]``
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
            //
            var obj = {
                // new message id
                mid: this.new_mid(options),
                action: options.action || lux.CrudMethod[options.crud] || options.crud,
                model: options.model,
                data: options.data
            };
            obj = JSON.stringify(obj);
            if (this._opened) {
                this._transport.send(obj);
            } else {
                this._queue.push(obj);
            }
        },
        //
        // Handle incoming messages
        onmessage: function (e) {
            var obj = JSON.parse(e.data),
                mid = obj.mid,
                options = mid ? this._pending_messages[mid] : undefined,
                data = obj.data;
            if (options) {
                delete this._pending_messages[mid];
                if (options.item) {
                    data = data[0];
                }
            }
            if (obj.error) {
                if (options && options.error) {
                    options.error(obj.error, this, obj);
                } else {
                    logger.error(this.toString() + ' - ' + obj.error);
                }
            } else {
                if (options && options.success) {
                    options.success(data, this, obj);
                } else {
                    logger.warning(
                        this.toString() + ' - Got message with no callback registered');
                }
            }
        },
        //
        // The socket is closed
        // If enabled, it auto-reconnects with an exponential back-off
        onclose: function () {
            this._opened = false;
            logger.warning(this + ' closed.');
            this.reconnect();
        },
        //
        // Create a new message id and add the options object to the
        // pending messages object
        new_mid: function (options) {
            if (options.success || options.error) {
                var mid = lux.s4();
                while (this._pending_messages[mid]) {
                    mid = lux.s4();
                }
                this._pending_messages[mid] = options;
                return mid;
            }
        },
        //
        websocket_uri: function (url) {
            var loc = window.location;
            if (!url) {
                url = loc.href.split('?')[0];
            }
            if (url.substring(0, 7) === 'http://') {
                return 'ws://' + url.substring(7);
            } else if (url.substring(0, 8) === 'https://') {
                return 'wss://' + url.substring(8);
            } else {
                if (url.substring(0, 5) === 'ws://' || url.substring(0, 6) === 'wss://') {
                    return url;
                } else {
                    var protocol = loc.protocol === 'http:' ? 'ws:' : 'wss:';
                    return lux.utils.urljoin(protocol, loc.host, loc.pathname, url);
                }
            }
        }
    });
    //
    register_store('ws', Socket);
    register_store('wss', Socket);
    //