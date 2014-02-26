
    var
    //
    BUTTON_SIZES = ['large', 'normal', 'small', 'mini'],
    //
    buttonGroup = lux.buttonGroup = function (options) {
        options || (options = {});
        var elem = $(document.createElement('div'));
        if (options.vertical) elem.addClass('btn-group-vertical');
        else elem.addClass('btn-group');
        if (options.radio) {
            elem.data('toggle', 'buttons-radio');
        }
        return elem;
    },
    //
    Button = lux.Button = lux.createView('button', {
        //
        tagName: 'button',
        //
        selector: '.btn',
        //
        defaults: {
            skin: 'default'
        },
        //
        className: 'btn',
        //
        initialise: function (options) {
            var btn = this.elem;
            btn.addClass(this.className).attr({
                type: options.type,
                title: options.title,
                href: options.href,
            }).addClass(options.classes);
            //
            this.setSkin(options.skin);
            this.setSize(options.size);
            if (options.text) btn.html(options.text);
            if (options.icon) lux.addIcon(btn, options);
            if (options.block) btn.addClass('btn-block');
        },
        //
        setSize: function (size) {
            if(BUTTON_SIZES.indexOf(size) > -1) {
                var elem = this.elem,
                    prefix = this.className + '-';
                _(BUTTON_SIZES).forEach(function (size) {
                    elem.removeClass(prefix + size);
                });
                elem.addClass(prefix + size);
            }
        }
    });