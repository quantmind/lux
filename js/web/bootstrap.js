    //
    // Alerts
    web.extension('alert', {
        selector: 'div.alert',
        defaultElement: 'div',
        options: {
            message: null,
            type: null,
            skin: null,
            closable: true
        },
        decorate: function () {
            var elem = this.element().addClass('alert').addClass(this.options.skin),
                options = this.options,
                self = this;
            if (options.message) {
                elem.html(options.message);
            }
            options.skin = this.get_skin();
            if (options.closable) {
                var close = web.create_button({
                    icon: 'remove',
                    skin: options.skin,
                    size: 'mini'}).addClass('right');
                elem.append(close);
                close.click(function() {
                    self.fadeOut(function() {
                        self.destroy();
                    });
                });
            }
        }
    });
    
    web.extension('tooltip', {
        selector: '.tooltip',
        decorate: function () {
            this.element().tooltip(this.options);
        }
    });