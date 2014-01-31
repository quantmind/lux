
lux.plugin('ajax', {
    isdefault: true,
    defaults: {
        autoload: true,
        responsetype: 'json',
        requestMethod: 'get',
        parsedata: null,
        url: '.'
    },
    tools: {
        'reload': {
            classname: 'reload',
            title: "Refresh data",
            icon: {
                'jquery': "ui-icon-refresh",
                'fontawesome': 'icon-repeat'
            },
            text: false,
            decorate: function (b, instance) {
                b.click(function (e, o) {
                    var inst = $.ecoplot.instance(this);
                    instance.container().trigger('load');
                });
            }
        }
    },
    init: function () {
        var self = this;
        self.container().bind('load', function () {
            self.ajaxload();
        });
    },
    ajaxload: function () {
        
    },
    parse_data: function (data) {
        
    }
});