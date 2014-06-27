    //
    //  Ajax Links & buttons
    //  ------------------------
    //
    web.extension('ajax', {
        selector: 'a.ajax, button.ajax',
        options: {
            dataType: 'json',
            success: null,
            error: null
        },
        //
        decorate: function () {
            var elem = this.element(),
                url = elem.is('a') ? elem.attr('href') : elem.data('href'),
                action = elem.data('action') || 'get',
                options = this.options,
                success = options.success,
                error = options.error,
                self = this;
            options.type = action;
            options.success = function (o, s, xhr) {
                self.on_success(o, s, xhr);
                if (success) {
                    success(o, s, xhr);
                }
            };
            elem.click(function (e) {
                e.preventDefault();
                $.ajax(url, options);
            });
        },
        //
        on_success: function (o, s, xhr) {
            if (o.redirect) {
                window.location = o.redirect;
            }
        }
    });