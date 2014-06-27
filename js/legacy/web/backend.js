    //
    // Create a new backend for lux web
    web.extension('backend', {
        defaultElement: 'div',
        defaults: {
            store: null,
            hartbeat: 0
        },
        //
        decorate: function () {
            var self = this,
                options = self.options,
                slice = Array.prototype.slice,
                url = options.host,
                socket_options = {
                    resource: options.resource
                };
            //
            if (options.hartbeat) {
                socket_options.onopen = function () {
                    // Add the backend element to the status bar
                    self.check_status();
                };
            }
            //
            self.element().addClass('socket-control').css({float: 'left'});
            self.socket = lux.create_store(options.store);
        },
        //
        check_status: function () {
            var self = this;
            self.socket.send({
                type: 'status',
                success: function () {
                    self.status.apply(self, arguments);
                },
                error: function (data) {
                    self.status.apply(self, arguments);
                }
            });
        },
        //
        // Implement the status message for the "status" channel.
        status: function (data, b, obj) {
            var self = this;
            if (obj.error) {
                self.element().html(data);
            } else if (data.uptime !== undefined) {
                self.element().html(lux.utils.prettyTime(data.uptime));
            }
            lux.eventloop.call_later(self.options.hartbeat, function () {
                self.check_status();
            });
        }
    });
