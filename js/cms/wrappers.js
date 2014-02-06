    //
    //  Default CMS Wrappers
    //  --------------------------------

    lux.cms.create_wrapper('well', {
        title: 'Well',
        render: function (elem) {
            return $("<div class='well'></div>").appendTo(elem);
        }
    });

    lux.cms.create_wrapper('welllg', {
        title: 'Well Large',
        render: function (elem) {
            return $("<div class='well-lg'></div>").appendTo(elem);
        }
    });

    lux.cms.create_wrapper('wellsm', {
        title: 'Well Small',
        render: function (elem) {
            return $("<div class='well-sm'></div>").appendTo(elem);
        }
    });

    lux.cms.create_wrapper('panel', {
        title: 'Panel',
        render: function (elem) {
            return elem.wrap("<div class='panel-body'></div>")
                       .wrap("<div class='panel panel-default'></div>");
        }
    });

    lux.cms.create_wrapper('paneltitle', {
        title: 'Panel with Title',
        render: function (elem) {
            var p = elem.wrap(
                "<div class='panel-body'></div>").wrap(
                "<div class='panel panel-default'></div>");
            return p;
        }
    });