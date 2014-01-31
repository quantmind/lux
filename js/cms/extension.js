    //
    //  lux web CMS extension
    //  --------------------------------
    //
    //  This is the javascript handler of ``lux.extensions.cms``.
    //  Updates to the backend are either via a websocket or ajax requests.
    lux.web.extension('cms', {
        selector: 'div.cms-page',
        //
        options: {
            editing: false,
            // backend type, choose websocket if possible
            backend_url: null,
            // icon for the button which add a new row in a grid
            add_row_icon: 'columns',
            // icon for the button which add a new block in a column
            add_block_icon: 'plus',
            //
            skin: 'control',
            //
            row_control_class: 'add-row',
            //
            columns: 24,
            //
            // Options for the dialog controlling page inputs
            page: {
                collapsable: true,
                collapsed: true,
                class_name: 'control',
                skin: 'inverse',
                buttons: {
                    size: 'default'
                }
            },
            // Options for the dialog controlling one grid
            grid: {
                collapsable: true,
                skin: null,
                class_name: 'control',
                buttons: {
                    size: 'default'
                }
            },
            // Options for the row dialog
            row: {
                closable: true,
                collapsable: true,
                skin: 'default',
                size: 'mini',
                dragdrop: false,
                dropzone: 'row-control'
            },
            // Options for the block dialog
            block: {
                closable: true,
                collapsable: true,
                skin: 'primary',
                size: 'mini',
                dragdrop: true,
                dropzone: 'block-control'
            }
        },
        //
        // The decorator called by ``lux.web``
        decorate: function () {
            var self = this,
                options = self.options,
                elem = self.element(),
                control = $('.cms-control');
            // In editing mode, set-up grids
            if (options.editing) {
                //self._handle_close();
                elem.addClass('editing');
                //
                // Create backend
                self.backend = web.backend({
                    host: options.backend_url,
                    hartbeat: 5
                });
                //
                lux.cms.set_transport(self.backend.socket);
                lux.cms.get(options.editing, {
                    success: function (page) {
                        self.view = new PageView(page[0], self);
                        self.view.render();
                    }
                });
            } else {
                self.view = new PageView(null, this);
                self.view.render();
            }
        },
        //
        _handle_close: function () {
            $(window).bind('beforeunload', function (e) {
                e.preventDefault();
                return false;
            });
        }
    });

    //  lux web grid CMS decorator
    //  -----------------------------------------
    //
    lux.web.extension('grid', {
        defaultElement: 'div',
        //
        options: {
            template: 'Half-Half',
            columns: 24
        },
        //
        decorate: function () {
            var template = ROW_TEMPLATES.get(this.options.template),
                options = this.options,
                elem = this.element();
            if (!template) {
                this.options.template = 'Half-Half';
                template = ROW_TEMPLATES.get(this.options.template);
            }
            this.template = template;
            elem.addClass('row grid'+this.options.columns);
            _(this.template).forEach(function (width) {
                var span = width*options.columns,
                    col = $(document.createElement('div')).addClass('column span'+span);
                elem.append(col);
            });
        }
    });