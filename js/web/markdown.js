
    web.extension('markdown', {
        selector: '.markdown',
        defaultElement: 'div',
        options: {
            extensions: ['prettify']
        },
        //
        decorate: function () {
            var element = this.element().addClass('markdown'),
                extensions = this.options.extensions,
                validextensions = [],
                raw = element.html(),
                requires = ['showdown'],
                extension;
            element.html('');
            if (extensions.indexOf('prettify') > -1) requires.push('prettify');
            require(requires, function () {
                // Add extensions
                _(extensions).forEach(function (name) {
                    extension = lux.showdown[name];
                    if (typeof(extension) === 'function') {
                        Showdown.extensions[name] = extension;
                        validextensions.push(name);
                    }
                });
                //
                var converter = new Showdown.converter({'extensions': validextensions}),
                    html = converter.makeHtml(raw);
                element.html(html);
                if (window.prettyPrint) {
                    window.prettyPrint(function () {
                        web.refresh(element);
                    }, element[0]);
                }
                else {
                    web.refresh(element);
                }
            });
        }
    });