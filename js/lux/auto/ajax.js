    //  Ajax Links & buttons
    //  ------------------------
    var ajax_on_success = function (o, s, xhr) {
        if (o.redirect) {
            window.location = o.redirect;
        }
    };

    lux.ajaxElement = function (elem) {
        var url = elem.is('a') ? elem.attr('href') : elem.data('href'),
            options = {
                type: elem.data('action') || 'get',
                success: ajax_on_success
            };
        elem.click(function (e) {
            e.preventDefault();
            $.ajax(url, options);
        });
    };

    lux.autoViews.push({
        selector: '[data-ajax="true"]',
        load: function(elem) {
            lux.ajaxElement($(elem));
        }
    });