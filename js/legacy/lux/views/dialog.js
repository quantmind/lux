    //  Dialog
    //  -----------------------
    var Dialog = lux.Dialog = lux.createView('dialog', {
        //
        jQuery: true,
        //
        selector: '.dialog',
        //
        defaultElement: 'div',
        //
        default_modals: {
            backdrop: true,
            keyboard: true,
            width: 400
        },
        //
        defaults: {
            // Specialised class name for this dialog
            className: null,
            show: true,
            keyboard: true,
            // Can the dialog be closed
            closable: null,
            // Can the dialog be collapsable
            collapsable: false,
            // If ``collapsable`` is ``true``, this parameter controls how the
            // dialog is rendered the first time.
            collapsed: false,
            dragdrop: false,
            fullscreen: false,
            title: null,
            body: null,
            footer: null,
            // To create a modal dialog
            modal: false,
            autoOpen: true,
            // Default width
            width: null,
            height: null,
            top: null,
            skin: 'default',
            icons: {
                open: 'plus-circle',
                close: 'minus-circle',
                remove: 'times',
                fullscreen: 'arrows-alt'
            },
            buttons: {
                size: 'mini'
            }
        },
        // Create the dialog
        initialise: function (options) {
            var self = this,
                elem = this.elem.addClass('dialog').addClass(
                    options.className).hide(),
                closable = options.closable,
                title = elem.attr('title') || options.title,
                header = $(document.createElement('div')).addClass('header'),
                wrap = $(document.createElement('div')).addClass('body-wrap'),
                h3 = $(document.createElement('h3')),
                toggle;
            //
            this.setSkin(options.skin);
            //
            this._body = $(document.createElement('div')).addClass(
                'body').append(elem.contents());
            this._foot = null;
            self.buttons = $(document.createElement('div')).addClass(
                'btn-group').addClass('pull-right');
            header.append(self.buttons).append(h3);
            if (title) {
                h3.append(title);
            }
            elem.empty().append(header).append(wrap.append(this._body));
            if (options.body) {
                this._body.append(options.body);
            }
            //
            this.createButton = function (opts) {
                opts = _.extend(opts || {}, options.buttons);
                if (!opts.skin) opts.skin = this.getSkin();
                return new Button(opts);
            };
            //
            // Add additional options
            if (options.modal) self._addModal(options);
            if (options.width) elem.width(options.width);
            if (options.height) this._body.height(options.height);
            if (options.collapsable) self._addCollapsable(options);
            if (options.closable) this._addClosable(options);
            if (options.fullscreen) this._addFullscreen(options);
            if (options.movable) this._addMovable(options);
            if (options.autoOpen) self.render();
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
            return this.elem.children('.header');
        },
        //
        title: function (value) {
            return this.header().children('h3').html(value);
        },
        //
        render: function () {
            this.fadeIn();
        },
        //
        //  INTERNALS
        //
        //
        _addModal: function (options) {
            var
            self = this,
            opts = _.extend({}, self.default_modals,
                _.isObject(options.modal) ? options.modal : null),
            modal = $(document.createElement('div')).attr({
                tabindex: -1,
                role: 'dialog'
            }).addClass('modal fullscreen').hide().appendTo(document.body),
            backdrop = $(document.createElement('div')).addClass(
                'modal-backdrop fullscreen'),
            ename = this.eventName('click');
            //
            modal.on(ename, function (e) {
                self.fadeOut();
            });
            this.elem.off(ename).on(ename, function (e) {
                e.stopPropagation();
            });
            if (opts.keyboard) {
                ename = this.eventName('keyup');
                modal.off(ename).on(ename, function (e) {
                    e.which === 27 && self.fadeOut();
                });
            }
            //
            this.enforceFocus();
            options.collapsable = false;
            options.width = options.width || opts.width;
            options.closable = options.closable === null ? true : options.closable;
            this.elem.appendTo(modal).addClass('dialog-modal')
            .on('remove', function () {
                backdrop.remove();
                modal.remove();
            }).on('show', function () {
                if (opts.backdrop)
                    backdrop.appendTo(document.body);
                modal.show();
                $(document.body).addClass('modal-open');
            }).on('hide', function () {
                modal.hide();
                backdrop.detach();
                $(document.body).removeClass('modal-open');
            });
        },
        //
        // make the dialog closable, unless it is already closable.
        // The optional ``options``  can specify:

        //  * ``destroy``, if true the dialog is removed when
        //    closed otherwise it is just fadeOut. Default ``True``.
        _addClosable: function (options) {
            var
            destroy = options.destroy,
            self = this,
            close = this.createButton({
                icon: options.icons.remove
            });
            close.elem.appendTo(this.buttons).click(function() {
                self.fadeOut({
                    complete: function () {
                        destroy ? self.destroy() : self.hide();
                    }
                });
            });
        },
        // Make this dialog collapsable
        _addCollapsable: function (options) {
            var self = this,
                body = this.elem.children('.body-wrap'),
                button = self.createButton(),
                hidden = false;
            // If the dialog starts life as already collapsed, avoid to show
            // the transaction by hiding the body. This requires a little trick
            // which involve removing the `collapse` class when the `hide` event
            // is triggered.
            if (options.collapsed) {
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
                self.elem.removeClass('collapsed');
                lux.addIcon(button.elem, {icon: options.icons.close});
            }).on('hidden', function () {
                self.elem.addClass('collapsed');
                lux.addIcon(button.elem, {icon: options.icons.open});
            });
            // make sure height is auto when the dialog is not collapsed at startupSSSSS
            if (!options.collapsed) {
                body.height('auto');
            }
            button.elem.appendTo(this.buttons).mousedown(function (e) {
                e.stopPropagation();
            }).click(function () {
                body.collapse('toggle');
                return false;
            });
            require(['bootstrap'], function () {
                self.elem.children('.body-wrap').collapse();
            });
        },
        //
        // Add full screen button and action
        _addFullscreen: function (options) {
            var
            fullscreen = options.fullscreen,
            button = this.createButton({
                icon: options.icons.fullscreen,
                title: 'Full screen mode'
            });
            if (!fullscreen.render) {
                // default full screen
                fullscreen = new Fullscreen({elem: this.body()});
            }
            button.elem.prependTo(this.buttons).on('click', function () {
                fullscreen.render();
            });
        },
        //
        _addMovable: function (options) {
            //var dragdrop = this.options.dragdrop;
            //if (dragdrop) {
            //    dragdrop.add(this.elem, this.header());
            //}
        }
    });
