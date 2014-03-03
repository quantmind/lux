
    var icons = lux.icons = {
        //
        fontawesome: function (elem, options) {
            var i = $('i', elem).remove(),
                ni = '<i class="fa fa-' + options.icon + '"></i>';
            if (elem[0].text) {
                elem[0].text = ' ' + elem[0].text;
            }
            elem.prepend(ni);
        }
    };

    lux.addIcon = function (elem, options) {
        var p = lux.icons[lux.icon];
        if (p && !elem.is('html')) {
            if (!options) options = elem.data();
            if (options.icon) p(elem, options);
        }
    };

    lux.autoViews.push({
        selector: '[data-icon]',
        load: function(elem) {
            lux.addIcon($(elem));
        }
    });