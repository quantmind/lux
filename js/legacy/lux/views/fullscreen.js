    //
    // Add full-screen
    var Fullscreen = lux.Fullscreen = lux.createView('fullscreen', {
        //
        defaults: {
            zindex: 2010,
            icon: 'times-circle',
            themes: ['default', 'inverse']
        },
        //
        initialise: function (options) {
            var container = $(document.createElement('div')).addClass(
                    'fullscreen').css({'z-index': options.zindex});

            this.wrap = $(document.createElement('div')).addClass(
                'fullscreen-container').appendTo(container);
            this.side = $(document.createElement('div')).addClass(
                'fullscreen-sidebar').appendTo(container);
            this.sidebar = buttonGroup({vertical: true}).appendTo(this.side);
            //
            this.themes = options.themes;
            this.theme = 1;
            this.exit = new Button({
                icon: options.icon,
                title: 'Exit full screen'
            });
            this.exit.elem.appendTo(this.sidebar);
            this.theme_button = new Button({
                icon: 'laptop',
                title: 'theme'
            });
            this.theme_button.elem.appendTo(this.sidebar);
            //
            this._wrapped = {
                elem: this.elem,
                previous: this.elem.prev(),
                parent: this.elem.parent()
            };
            //
            this.setElement(container);
            this.toggle_skin();
        },
        //
        render: function () {
            var self = this;
            if (!self.elem.parent().length) {
                //
                self.exit.elem.click(function () {
                    self.remove();
                });
                //
                self.theme_button.elem.click(function () {
                    self.toggle_skin();
                });
                self.wrap.append(this._wrapped.elem);
                self.elem.appendTo(document.body);
            }
        },
        //
        remove: function () {
            var w = this._wrapped;
            if(w.previous.length) {
                w.previous.after(w.elem);
            } else {
                w.parent.prepend(w.elem);
            }
            return this._super();
        },
        //
        toggle_skin: function () {
            var themes = this.themes,
                old_theme = this.theme;
            this.theme = old_theme ? 0 : 1;
            this.theme_button.setSkin(themes[old_theme]);
            this.setSkin(themes[this.theme]);
        }
    });
