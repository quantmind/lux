    //  Ajax Links & buttons
    //  ------------------------
    //
    lux.ajaxResponses = [];
    //
    lux.ajaxResponse = function (o, code, jqXHR) {
        _(lux.ajaxResponses).forEach(function (response) {
            return response(o, jqXHR);
        });
    };

    lux.ajaxElement = function (elem) {
        var url = elem.is('a') ? elem.attr('href') : elem.data('href'),
            options = {
                type: elem.data('action') || 'get',

                success: lux.ajaxResponse
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

    //
    lux.ajaxResponses.push(function (o, status, jqXHR) {
        if (o.redirect) {
            window.location = o.redirect;
            return true;
        }
    });

    //
    lux.ajaxResponses.push(function (o, status, jqXHR) {
        if (o.html) {
        }
    });