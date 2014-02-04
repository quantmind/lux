    //  Dialog
    //  -----------------------
    web.extension('dialog', {
        //requires: ['bootstrap'],
        selector: 'div.dialog',
        defaultElement: 'div',
        options: {
            class_name: null,
            show: true,
            keyboard: true,
            closable: null,
            collapsable: false,
            // If ``collapsable`` is ``true``, this parameter controls how the
            // dialog is rendered the first time.
            collapsed: false,
            dragdrop: false,
            fullscreen: false,
            title: null,
            body: null,
            footer: null,
            modal: false,
            modal_zindex: 1040,
            popup: null,
            autoOpen: true,
            width: null,
            height: null,
            top: null,
            skin: null,
            icons: {
                open: 'plus-sign',
                close: 'minus-sign',
                remove: 'remove',
                fullscreen: 'fullscreen'
            },
            buttons: {
                size: 'mini'
            }
        },
        // Create the dialog
        decorate: function () {
            var self = this,
                options = self.options,
                elem = self.element().addClass('dialog')
                        .addClass(options.class_name).addClass(options.skin),
                closable = options.closable,
                popup = options.popup,
                title = elem.attr('title') || options.title,
                header = $(document.createElement('div')).addClass('header'),
                wrap = $(document.createElement('div')).addClass('body-wrap'),
                h3 = $(document.createElement('h3')),
                toggle;
            this._body = $(document.createElement('div')).addClass('body').append(elem.contents());
            this._foot = null;
            options.skin = this.get_skin();
            self.buttons = $(document.createElement('div')).addClass('btn-group').addClass('right');
            header.append(self.buttons).append(h3);
            if (title) {
                h3.append(title);
            }
            elem.empty().append(header).append(wrap.append(this._body));
            if (options.body) {
                this._body.append(options.body);
            }
            //
            // Modal option
            var width = options.width;
            if(options.modal) {
                width = width || 500;
                elem.css({
                    'margin-left': -width/2 + 'px',
                    'left': '50%',
                    'position': 'absolute',
                    'z-index': options.modal_zindex + 10,
                    'top': options.top || '25%'
                }).appendTo(document.body);
                popup = false;
                closable = closable === null ? true : closable;
                var backdrop = $(document.createElement('div'))
                                    .addClass('modal-backdrop fullscreen')
                                    .css('z-index', options.modal_zindex);
                elem.on('remove', function () {
                    backdrop.remove();
                }).on('show', function () {
                    backdrop.appendTo(document.body);
                }).on('hide', function () {
                    backdrop.detach();
                });
            }
            if (elem.parent().length === 0) {
                popup = true;
            }
            if (popup) {
                elem.appendTo(document.body);
            }
            // set width
            if (width) {
                elem.width(width);
            }
            // set height
            if (options.height) {
                this._body.height(options.height);
            }
            // Add collapsable stuff
            if (options.collapsable) {
                var collapse_button = self.collapsable();
                self.buttons.append(collapse_button);
            }
            // Add close stuff
            if (closable) {
                options.closable = false;
                this.closable(closable);
            }
            //
            // Full screen
            self.fullscreen();
            // Movable
            self.make_movable();
            //
            if(options.autoOpen) {
                self.fadeIn();
            }
            elem.addClass('ready');
        },
        //
        body: function () {
            return this._body;
        },
        //
        foot: function () {
            return this._foot;
        },
        //
        header: function () {
            return this.element().children('.header');
        },
        //
        title: function (value) {
            return this.header().children('h3').html(value);
        },
        //
        create_button: function (opts) {
            opts = $.extend(opts || {}, this.options.buttons);
            if (!opts.skin) {
                opts.skin = this.options.skin;
            }
            return web.create_button(opts);
        },
        //
        // make the dialog closable, unless it is already closable.
        // The optional ``options``  can specify:

        //  * ``destroy``, if true the dialog is removed when
        //    closed otherwise it is just fadeOut. Default ``True``.
        closable: function (options) {
            var destroy = true;
            if (_.isObject(options)) {
                options = _.extend({destroy: true}, options);
                destroy = options.destroy;
            }
            if (!this.options.closable) {
                var self = this;
                this.options.closable = true;
                var close = this.create_button({icon: this.options.icons.remove});
                this.buttons.append(close);
                close.click(function() {
                    self.fadeOut(function() {
                        if (destroy) {
                            self.destroy();
                        }
                    });
                });
            }
        },
        // Make this dialog collapsable
        collapsable: function () {
            var self = this,
                body = this.element().children('.body-wrap'),
                button = self.create_button(),
                hidden = false;
            // If the dialog starts life as already collapsed, avoid to show
            // the transaction by hiding the body. This requires a little trick
            // which involve removing the `collapse` class when the `hide` event
            // is triggered.
            if (this.options.collapsed) {
                hidden = true;
                body.hide().addClass('in').one('hide', function () {
                    body.removeClass('collapse');
                });
            }
            body.on('show', function () {
                if (hidden) {
                    hidden = false;
                    body.addClass('collapse').show();
                }
                self.element().removeClass('collapsed');
                web.icon(button, self.options.icons.close);
            }).on('hidden', function () {
                self.element().addClass('collapsed');
                web.icon(button, self.options.icons.open);
            }).collapse();
            // make sure height is auto when the dialog is not collapsed at startupSSSSS
            if (!this.options.collapsed) {
                body.height('auto');
            }
            button.mousedown(function (e) {
                e.stopPropagation();
            }).click(function () {
                body.collapse('toggle');
                return false;
            });
            return button;
        },
        //
        // Add full screen button and action
        fullscreen: function () {
            var self = this,
                fullscreen = self.options.fullscreen;
            if (fullscreen) {
                var button = self.create_button({
                    icon: self.options.icons.fullscreen,
                    title: 'Full screen mode'
                });
                if (!$.isFunction(fullscreen)) {
                    // default full screen
                    fullscreen = function () {
                        web.fullscreen(this.body());
                    };
                }
                self.buttons.prepend(button);
                button.click(function () {
                    fullscreen.call(self);
                });
            }
        },
        //
        make_movable: function () {
            //var dragdrop = this.options.dragdrop;
            //if (dragdrop) {
            //    dragdrop.add(this.element(), this.header());
            //}
        }
    });

    $.fn.dialog = function (options) {
        return this.each(function() {
            web.dialog(this, options);
        });
    };