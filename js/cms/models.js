    //
    //  LUX CMS
    //  ---------------------------------

    //  Inline editing and drag & drop for blocks within a page. The layout
    //  starts with a Page which contains a given set of ``Grid`` components
    //  which are managed the ``GridView`` model.
    //
    //  Each ``Grid`` contains one or more ``Row`` components which can be added
    //  interactively. A row has several templates with a predefined set of
    //  ``Columns``.
    var ROW_TEMPLATES = new lux.Ordered(),
        BLOCK_TEMPLATES = new lux.Ordered(),
        content_type = 'content_type',
        dbfields = 'dbfields',
        web = lux.web;
    //
    // Content Model
    // ----------------

    // Base class for contents.
    // A new content class is created via the higher level utility function
    // ``cms.create_content_type``.
    // A content can be persistent (its data is stored in a database) or not.
    // A non-persistent content stores its data in the page layout,
    // while the persistent one has also its own database representation.
    // To mark a model persistent, add the ``persistent: true`` attribute to
    // the ``meta`` object in the class definition.
    var Content = cms.Content = lux.Model.extend({
        show_title: false,
        //
        meta: {
            name: 'content',
            //
            fields: {
                created: null,
                //
                timestamp: null,
                //
                id: new lux.Field({
                    type: 'hidden',
                    fieldset: {Class: dbfields}
                }),
                title: new lux.Field({
                    required: 'required',
                    placeholder: 'title',
                    fieldset: {Class: dbfields}
                }),
                keywords: new lux.KeywordsField({
                    placeholder: 'keywords',
                    fieldset: {Class: dbfields}
                })
            }
        },
        //
        // Create a jQuery Form element for customising the content.
        // Each subclass of Content can implement this method which by default
        // returns an empty form with the submit button.
        get_form: function () {},
        //
        // Render this Content into a `container`. Must be implemented
        // by subclasses
        render: function (container) {},
        //
        close: function () {
            if (this.container) {
                this.container.trigger('close-plugin-edit');
                delete this.container;
            }
        },
        //
        // Sync only if the content is persistent in the backend,
        // otherwise no need to do anything
        sync: function (store, options) {
            this.set(content_type, this._meta.name);
            if (this._meta.persistent) {
                return this._super(store, options);
            } else {
                if (options && options.success) {
                    options.success.call(this._meta, this.fields());
                }
            }
        },
        //
        // Serialize the content.
        //
        // Used by the PositionView when sychronosing with backend
        serialize: function() {
            if (this._meta.persistent) {
                var pk = this.pk();
                if (pk) {
                    return pk;
                }
            } else {
                this.set(content_type, this._meta.name);
                return this.fields();
            }
        }
    });
    //
    // Wrapper Model
    // ----------------

    // Base class for html wrappers
    var Wrapper = cms.Wrapper = lux.Class.extend({
        render: function (view) {
            view.content.render(view.elem);
        }
    });
    //
    // Page Model
    // ----------------

    // A container of ``Content`` models displaied on a grid.
    var Page = lux.Model.extend({
        meta: cms,
        //
        // Got new content update
        update_content: function (o) {
            var id = o.id,
                data = o.data;
            if (id && data) {
                var ContentType = this.content_type(data.content_type);
                if (ContentType) {
                    var meta = ContentType.prototype._meta;
                    return meta.update(id, data);
                }
            }
            web.logger.error('Could not understand content');
        }
    });
