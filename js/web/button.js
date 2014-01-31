
    // Object containing Icon providers
    web.iconProviders = {
        fontawesome: {
            icon: function (elem, name) {
                elem.data('iconProvider', 'fontawesome');
                var i = $('i', elem),
                    ni = '<i class="icon-' + name + '"></i>';
                if (i.length) {
                    i.replaceWith(ni);
                } else {
                    elem.prepend(ni);
                }
            }
        }
    };
    web.BUTTON_SIZES = ['large', 'normal', 'small', 'mini'];

    // Icon manager. Uses lux.web.options.icon for the provider
    web.icon = function (elem, name, options) {
        var pname;
        if (options) {
            pname = options.iconProvider || elem.data('iconProvider') || web.options.icon;
        } else {
            pname = elem.data('iconProvider') || web.options.icon;
        }
        web.iconProviders[pname].icon(elem, name);
    };

    //  Create a button
    //  ---------------------
    //
    //  Create a ``<a class='btn'>`` element with the following ``options``:
    //
    //  * ``size``: the size of the button, one of ``large``, ``normal`` (default),
    //    ``small`` or ``mini``.
    //  * ``skin``: optional skin to use. One of ``default`` (default), ``primary``,
    //    ``success``, ``error`` or ``inverse``.
    //  * ``text`` the text to display.
    //  * ``title`` set the title attribute.
    //  * ``classes`` set additional Html classes.
    //  * ``icon`` icon name to include.
    //  * ``block`` if ``true`` add the ``btn-block`` class for block level buttons,
    //    those that span the full width of a parent.
    //  * ``tag`` to specify a different tag from ``a``.
    //  * ``type`` add the type attribute (only when the tag is ``button`` or ``input``).
    //  * ``data`` optional object to attach to the data holder.
    lux.web.create_button = function (options) {
        options = options ? options : {};
        var tag = (options.tag || 'a').toLowerCase(),
            btn = $(document.createElement(tag));
        btn.addClass('btn');
        btn.attr('type', options.type);
        btn.attr('title', options.title);
        btn.addClass(options.classes);
        btn.attr('href', options.href);
        if (options.size) {
            btn.addClass('btn-' + options.size);
        }
        if (options.skin && options.skin !== 'default') {
            btn.addClass(options.skin);
        }
        if (options.icon) {
            web.icon(btn, options.icon, options);
        }
        if (options.text) {
            btn.append(' ' + options.text);
        }
        if (options.block) {
            btn.addClass('btn-block');
        }
        if (options.data) {
            btn.data(options.data);
        }
        return lux.web.refresh(btn);
    };

    lux.web.button_group = function (options) {
        var elem = $(document.createElement('div')).addClass('btn-group');
        if (options.radio) {
            elem.data('toggle', 'buttons-radio');
        }
        return elem;
    };
