
$.lux.icon = function (text, fontawesome) {
    return {'text': text,
            'fontawesome': fontawesome};
};

$.lux.icons = {};
$.lux.icons.close = $.lux.icon('x', 'remove');
$.lux.icons.settings = $.lux.icon('settings', 'cogs');


$.lux.application('button', {
    selector: '.btn',
    defaults: {
        type: 'btn',
        text: true,
        icon: null,
        skin: null
    },
    defaultElement: '<button>',
    init: function () {
        var c = this.container(),
            options = this.options,
            icon_provider = $.lux.html.options.icon;
        if (options.icon && icon_provider) {
            var icon = $.lux.icons[options.icon] || options.icon,
                text = c.html();
            c.addClass(options.icon);
            if (icon_provider === 'fontawesome') {
                icon = icon.fontawesome || icon;
                icon = '<i class="icon-' + icon + '"></i>';
            } else {
                icon = icon.text || icon;
            }
            if (options.text && options.text !== true) {
                text = options.text;
            }
            if (options.text) {
                icon += text;
            }
            c.empty().append(icon);
        } else if (options.text && options.text !== true) {
            c.html(options.text);
        }
        c.addClass(options.type).addClass(options.skin);
    }
});
//
// A toolbar of groups of buttons and inputs
$.lux.application('toolbar', {
    selector: '.toolbar',
    defaultElement: '<div>',
    defaults: {
        type: 'orizontal',   // or 'vertical'
        groups: []  //  array of arrays containing element in the group
    },
    init: function () {
        var self = this,
            c = this.container(),
            groups = c.children();
        if (!groups.length) {
            $.each(this.options.groups || [], function () {
                var group = this,
                    div = $(document.createElement('div')).appendTo(c);
                $.each(group, function () {
                    var elem = self._create_entry(this);
                    div.append(elem);
                });
            });
        }
        c.children().addClass('group');
    },
    _create_entry: function (elem) {
        var o;
        if ($.isPlainObject(elem)) {
            var tag = elem.tag || 'button',
                options = elem;
            elem = $(document.createElement(tag));
            delete options.tag;
            if (elem.is('select')) {
                o = elem;
            } else {
                o = $.lux.button(elem, options).container();
            }
        } else {
            o = $(elem);
            if (o.length === 0) {
                o = $.lux.button({text: elem}).container();
            }
        }
        return o;
    }
});

$.lux.application('alert', {
    selector: '.alert',
    defaultElement: '<div>',
    init: function () {
        var self = this,
            close = self.container().find('.close');
        if (!close.length) {
            close = $.lux.button({icon:'close'}).container().addClass(self.skin());
        }
        close.addClass('btn-mini');
        self.container().prepend(close.addClass('right'));
        close.click(function () {
            self.destroy();
        });
    }
});


$.lux.application('tabs', {
    selector: '.tabs',
    defaultElement: '<div>',
    defaults: {
        position: null
    },
    init: function () {
        var self=  this,
            c = this.container(),
            position = this.options.position,
            bottom = this._removeClass('tabs-bottom'),
            left = this._removeClass('tabs-left'),
            right = this._removeClass('tabs-right'),
            current;
        if (!position) {
            if (bottom) {
                position = 'bottom';
            } else if (left) {
                position = 'left';
            } else if (right) {
                position = 'right';
            }
        }
        if (position === null) {
            position = 'top';
        }
        this.options.position = position;
        c.addClass('tabs-'+position);
        self._setup_links();
        c.children('ul').on('click', 'a', function (e) {
            e.preventDefault();
            self.changetab(e.target);
        });
        current = this._current();
        if (current.length !== 1) {
            var a = this.container().children('ul').find('a');
            if (a.length) {
                current = $(a[0]);
            }
        }
        current.click();
    },
    // Change the tab
    changetab: function (index) {
        index = $(index);
        if(index.is('a')) {
            var selector = index.data('div-selector'),
                c = this.container(),
                content = c.children('div.content'),
                div = content.children(selector);
            if (div.length === 1) {
                content.children().hide();
                c.children('ul').find('a').removeClass('active open');
                index.addClass('active open');
                div.show();
            }
        }
    },
    // Add tab to tabs
    add: function (tab, data) {
        var link = $.lux.utils.as_tag('a', tab),
            content = this.container().children('.content'),
            ul = this.container().children('ul');
        if (!data) {
            data = $('<div>');
        }
        if (!link.data('div-selector')) {
            var idx = ul.children().length + 1,
                href = this.id() + '_tab' + idx;
            data.attr('id', href);
            link.data('div-selector', '#' + href);
        }
        ul.append($('<li>').append(link));
        content.append(data);
        return link;
    },
    _setup_links: function () {
     // link ancors to divs
        var self = this,
            c = this.container(),
            ul = c.children('ul'),
            content = c.children('div.content'),
            divs;
        if (!content.length) {
            divs = c.children('div');
            content = $('<div>').addClass('content').appendTo(c);
        } else {
            divs = content.children('div');
        }
        divs = $('<div>').append(divs);
        content.empty();
        if (ul.length === 0) {
            ul = $('<ul>');
        }
        ul.addClass('nav');
        if (this.options.position === 'bottom') {
            c.append(ul);
        } else {
            c.prepend(ul);
        }
        var elems = ul.find('a'),
            js=0;
        ul.empty();
        elems.each(function () {
            var link = $(this);
            var href = link.attr('href');
            var div = divs.children(href);
            if (div.length !== 1) {
                for (; js < divs.length; js++) {
                    div = $(divs[js]);
                    if (div.data('link') === undefined) {
                        break;
                    }
                    div = null;
                }
            } else {
                link.data('div-selector', href);
            }
            self.add(link, div);
        });
    },
    _current: function () {
        return this.container().children('ul').find('a.active');
    },
    _removeClass: function (name) {
        var c = this.container(),
            has = c.hasClass(name);
        if (has) {
            c.removeClass(name);
        }
        return has;
    }
});