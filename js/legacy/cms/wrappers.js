    //
    //  Default CMS Wrappers
    //  --------------------------------

    var _panel = function (view, with_header, with_title) {
        var outer = $("<div class='panel panel-default'></div>").appendTo(view.elem).addClass(view.skin);
        if (with_header) {
            var head = $("<div class='header'></div>").appendTo(outer),
                title = view.content.get('title');
            if (with_title) {
                head = $("<h3 class='title'></h3>").appendTo(head);
            }
            if (title) {
                head.html(title);
            }
        }
        var elem = $("<div class='body'></div>").appendTo(outer);
        view.content.render(elem, view.skin);
    };


    cms.create_wrapper('nothing', {
        title: 'No Wrapper'
    });

    cms.create_wrapper('well', {
        title: 'Well',
        render: function (view) {
            var elem = $("<div class='well'></div>").appendTo(view.elem);
            view.content.render(elem);
        }
    });

    cms.create_wrapper('welllg', {
        title: 'Well Large',
        render: function (view) {
            var elem = $("<div class='well well-lg'></div>").appendTo(view.elem).addClass(view.skin);
            view.content.render(elem);
        }
    });

    cms.create_wrapper('wellsm', {
        title: 'Well Small',
        render: function (view) {
            var elem = $("<div class='well well-sm'></div>").appendTo(view.elem).addClass(view.skin);
            view.content.render(elem);
        }
    });

    cms.create_wrapper('panel', {
        title: 'Panel',
        render: function (view) {
            _panel(view);
        }
    });

    cms.create_wrapper('panelheading', {
        title: 'Panel with heading',
        render: function (view) {
            _panel(view, true);
        }
    });

    cms.create_wrapper('paneltitle', {
        title: 'Panel with title',
        render: function (view) {
            _panel(view, true, true);
        }
    });
