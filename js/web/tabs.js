// Tabs
//
//
web.extension('tabs', {
    selector: '.tabs',
    defaultElement: 'div',
    options: {
        layout: 'horizontal',
        tabs: null
    },
 // Create the tabs
    decorate: function () {
        var tabs = this,
            elem = tabs.element(),
            options = tabs.options,
            ul = elem.children('ul'),
            target = elem.children('div');
        //
        if (!ul.length && !target.length && options.tabs) {
            ul = $(document.createElement('ul')).appendTo(elem);
            target = $(document.createElement('div')).appendTo(elem);
        }
        // Process ul
        ul.find('a').each(function () {
            
        });
        //
        $.extend(tabs, {
            current: null,
            'target': function () {
                return target;
            },
            'ul': function () {
                return ul;
            },
            add_tab: function (tab) {
                self.add_tab(tabs, tab);
            }
        });
        //
        if (options.tabs) {
            $.each(options.tabs, function () {
                self.add_tab(tabs, this);
            });
        }
        self.select(tabs, 0);
    },
    //
    add_tab: function (tabs, tab) {
        var ul = tabs.ul(),
            target = tabs.target(),
            a = $(document.createElement('a')).attr('href', tab.link).html(tab.text);
        ul.append($(document.createElement('li')).append(a));
        a.click(function (), {
            if (tabs.current) {
                tabs.current.hide();
            }
            
        });
    },
    //
    select: fynction (tabs, index) {
        
    }
});