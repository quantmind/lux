    //
    //  lux web CMS extension
    //  --------------------------------
    //
    //  This is the javascript handler of ``lux.extensions.cms``.
    //  Updates to the backend are either via a websocket or ajax requests.
    var CmsView = lux.CmsView = lux.createView('cms', {
        //
        selector: '.cms-page',
        //
        defaults: {
            //
            editing: false,
            // backend url used to communicate with backend server
            // when updating & creating content as well as when
            // repositioning it
            backend_url: null,
            //
            // content url is used for AJAX retrieval of database contents
            content_url: null,
            //
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
            // Hart beat for websocket connections
            hartbeat: 5,
            //
            // Options for the dialog controlling page inputs
            page: {
                collapsable: true,
                collapsed: true,
                className: 'control',
                skin: 'inverse',
                buttons: {
                    size: 'default'
                }
            },
            // Options for the dialog controlling one grid
            grid: {
                collapsable: true,
                className: 'control',
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
            },
            // Options for content editing dialog
            contentedit: {
                modal: true,
                movable: true,
                fullscreen: true,
                autoOpen: false,
                width: 600,
                title: 'Edit Content',
                fade: {duration: 20},
                closable: {destroy: false}
            }
        },
        //
        // The decorator called by ``lux.web``
        initialise: function (options) {
            var self = this,
                elem = self._element;
            // In editing mode, set-up grids
            if (options.editing) {
                //self._handle_close();
                this.elem.addClass('editing');
                //
                options.store = new lux.create_store(
                    options.backend_url, {
                        hartbeat: options.hartbeat
                    });
                //if (options.store.type === 'websocket') {
                //   this.backend = web.backend({store: options.store});
                //}
            }
            this._setup_api();
            this._super(options);
        },
        //
        _setup_api: function () {
            var api = $('html').data('api');
            if (!api) {
                this.on_sitemap();
            } else {
                var self = this;
                $.ajax(api.url, {
                    dataType: 'json',
                    success: function (data, status, xhr) {
                        self.on_sitemap(api, data);
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        self.on_sitemap(api);
                    }
                });
            }
        },
        //
        // When the api sitemap is available, this method setup the
        // datatable content type.
        on_sitemap: function (api, sitemap) {
            var datatable = cms.content_type('datatable');
            if (datatable) {
                if (api) {
                    api.sitemap = sitemap;
                }
                datatable._meta.api_info(api);
            }
        },
        //
        _handle_close: function () {
            $(window).bind('beforeunload', function (e) {
                e.preventDefault();
                return false;
            });
        }
    }, PageView);
