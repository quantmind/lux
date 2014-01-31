    //
    // A smart select
    web.extension('select', {
        selector: 'select',
        defaultElement: 'select',
        //
        decorate: function () {
            var select = this,
                options = select.options,
                element = select.element(),
                temp;
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
    // Create a select element
    web.create_select = function (entries, options) {
        var elem = $(document.createElement('select'));
        elem.append($("<option></option>"));
        _(entries).forEach(function (o) {
            elem.append($("<option></option>").val(o.value).text(o.text || o.value));
        });
        return web.select(elem, options);
    };
