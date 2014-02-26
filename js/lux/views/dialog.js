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
        defaults: {
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
            modal: false,
            modal_zindex: 1040,
            autoOpen: true,
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
            if (!elem.attr('id')) elem.attr('id', this.cid);
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
            // Modal option
            var width = options.width;
            if(options.modal) {
                width = this._modalCss(options);
                elem.appendTo(document.body);
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
            // set width
            if (width) elem.width(width);
            // set height
            if (options.height) this._body.height(options.height);
            if (options.collapsable) self._addCollapsable(options);
            if (closable) this._addClosable(options);
            if (options.fullscreen) this._addFullscreen(options);
            if (options.movable) this._addMovable(options);
            if (options.autoOpen) self.show();
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
                self.element().addClass('collapsed');
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
            //    dragdrop.add(this.element(), this.header());
            //}
        },
        //
        _modalCss: function (options) {
            var width = options.width || 500;
            rules = ['#' + this.attr('id') + '{',
                     '    margin-left: -' + width/2 + 'px,',
                     '    left: 50%,',
                     '    position: absolute,',
                     'z-index: ' + (options.modal_zindex + 10) + ',',
                     'top: ' + (options.top || '25%'),
                     '}'];
            this.addStyle(rules);
            return width;
        }
    });
