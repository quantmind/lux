    //
    // Add full-screen 
    web.extension('fullscreen', {
        defaultElement: 'div',
        //
        options: {
            zindex: 2010,
            icon: 'remove'
        },
        //
        decorate: function () {
            var fullscreen = this,
                options = this.options,
                container = $(document.createElement('div')).addClass('fullscreen zen')
                                                            .css({'z-index': options.zindex}),
                element = this.element(),
                wrap = $(document.createElement('div')).addClass('fullscreen-container').appendTo(container),
                previous = element.prev(),
                parent = element.parent(),
                sidebar = $(document.createElement('div')).addClass('fullscreen-sidebar').appendTo(container),
                exit = web.create_button({
                    icon: options.icon,
                    title: 'Exit full screen'
                }).appendTo(sidebar);
            this._container = container;
            //
            exit.click(function () {
                if(previous.length) {
                    previous.after(element);
                } else {
                    parent.prepend(element);
                }
                fullscreen.destroy();
            });
            //
            wrap.append(element);
            container.appendTo(document.body);
        },
        //
        container: function () {
            return this._container;
        }
    });
        