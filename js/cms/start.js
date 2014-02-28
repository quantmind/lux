//
//  LUX CMS
//  ---------------------------------

//  This is a the fornt-end implementation of lux content management system
//  extension. It provides an easy and elegant way to add content to
//  pages. It includes:

//  * Inline editing
//  * drag & drop for content blocks within a page
//  * Extendibility using javascript alone

//  The layout starts with a Page which contains a given set of ``Grid``
//  components which are managed the ``GridView`` model.
//
//  Each ``Grid`` contains one or more ``Row`` components which can be added
//  interactively. A row has several templates with a predefined set of
//  ``Columns``.
define(['lux'], function (lux) {
    "use strict";

    var
    logger = lux.getLogger('cms'),
    //
    cms = lux.cms = {
        name: 'page',
        //
        _content_types: {},
        //
        _wrapper_types: {},
        //
        // retrieve a content type by name
        content_type: function (name) {
            return this._content_types[name];
        },
        //
        // retrieve a wrapper type by name
        wrapper_type: function (name) {
            return this._wrapper_types[name];
        },
        //
        // Return an array of Content types sorted by name
        content_types: function () {
            return this._sorted(this._content_types);
        },
        //
        // Return an array of Wrapper types sorted by name
        wrapper_types: function () {
            return this._sorted(this._wrapper_types);
        },
        //
        // Create a new Content model and add it to the available content
        // types.
        create_content_type: function (name, attrs, BaseContent) {
            var meta = attrs.meta;
            if (!BaseContent) {
                BaseContent = Content;
            }
            attrs.meta = attrs.meta || {};
            attrs.meta.name = name.toLowerCase();
            var ct = BaseContent.extend(attrs);
            this._content_types[ct._meta.name] = ct;
            return ct;
        },
        //
        // Create a new Html Wrapper model and add it to the available wrappers
        // types.
        create_wrapper: function (name, attrs, BaseWrapper) {
            if (!BaseWrapper) {
                BaseWrapper = Wrapper;
            }
            if (!attrs.title) {
                attrs.title = name;
            }
            attrs.name = name.toLowerCase();
            var NewWrapper = BaseWrapper.extend(attrs),
                wrapper = new NewWrapper();
            this._wrapper_types[wrapper.name] = wrapper;
            return wrapper;
        },
        //
        set_transport: function (backend) {
            this._backend = backend;
            _(this._content_types).forEach(function (ct) {
                ct._meta.set_transport(backend);
            });
        },
        //
        // Internal method used by `content_tyeps` and `wrapper_types`
        _sorted: function (iterable) {
            var sortable = [];
            _(iterable).forEach(function (ct) {
                if (ct._meta) {
                    ct = ct._meta;
                }
                sortable.push({value: ct.name, text: ct.title});
            });
            sortable.sort(function (a, b) {
                return a.text > b.text ? 1 : -1;
            });
            return sortable;
        }
    };
