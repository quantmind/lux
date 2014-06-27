    //  Tabs
    //  ----------------
    //
    //  Uses bootstrap ``tab`` component
    var TabView = lux.TabView = lux.View.extend({
        data_key: 'tabview',
        //
        initialise: function (options) {
            var self = this;
            //
            this.tabs = this.elem.children('ul');
            this.content = this.elem.children('div');
            if (!this.tabs.length) {
                this.tabs = $(document.createElement('ul'));
            }
            if (!this.content.length) {
                this.content = $(document.createElement('div'));
            }
            if (options.pills) {
                this.tabs.addClass('nav-pills');
            } else {
                this.tabs.addClass('nav-tabs');
            }
            this.elem.prepend(this.tabs.addClass('nav').addClass(options.skin));
            this.elem.append(this.content.addClass('tab-content'));
            //
            _(options.tabs).each(function (tab) {
                self.add_tab(tab);
            });

            require(['bootstrap'], function () {
                self.tabs.on('click', 'a', function (e) {
                    e.preventDefault();
                    $(this).tab('show');
                });
                self.activate_tab();
            });
        },

        add_tab: function (tab) {
            if (_.isString(tab)) {
                tab = {name: tab};
            }
            if (!tab.link) {
                tab.link = '#' + this.cid + '-' + tab.name;
            }
            var
            a = $(document.createElement('a')).attr({
                'href': tab.link,
                'id': this.cid + '-name-' + tab.name
            }).html(tab.name),
            pane = $(document.createElement('div')).addClass('tab-pane').html(tab.content);
            if (tab.link.substr(0, 1) === '#')
                pane.attr('id', tab.link.substr(1));
            this.tabs.append($(document.createElement('li')).append(a));
            this.content.append(pane);
        },

        activate_tab: function (tab) {
            var tabs = this.tabs.find('a');
            tab = tab ? tabs.find('#' + this.cid + '-name-' + tab) : tabs.first();
            tab.trigger('click');
        }
    });

    $.fn.tabs = function (options) {
        var view = this.data('tabview');
        if (!view) {
            options.elem = this;
            view = new TabView(options);
        }
        return view.elem;
    };
