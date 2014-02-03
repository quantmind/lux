    //
    // Select Extension
    // -----------------------

    // An extension to decorate ``select`` elements with the
    // [select2](http://ivaynberg.github.io/select2/) jquery plugin.
    // For ``options`` check the select2
    // [documentation](http://ivaynberg.github.io/select2/#documentation).
    //
    web.extension('select', {
        selector: 'select',
        defaultElement: 'select',
        //
        decorate: function () {
            var select = this,
                options = select.options,
                element = select.element(),
                temp;
            // This does not seems to work
            if (!element.parent().length) {
                temp = $(document.createElement('div')).append(element);
            }
            element.select2(options);
            if (temp) {
                this.container().detach();
            }
        },
        // Retrieve the select2 instance form the element
        select2: function () {
            return this.element().data('select2');
        },
        // Retrieve the select2 container
        container: function () {
            return this.select2().container;
        }
    });


    //
    // Create and return a ``select`` jQuery element with given ``options``.
    web.create_select = function (options) {
        var elem = $(document.createElement('select'));
        elem.append($("<option></option>"));
        _(options).forEach(function (o) {
            elem.append($("<option></option>").val(o.value).text(o.text || o.value));
        });
        return elem;
    };
