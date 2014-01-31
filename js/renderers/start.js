(function ($) {
"use strict";
var lux = $.lux,
    logger = lux.logger,
    math=  lux.math,
    PI = Math.PI,
    not_implemented = function (name) {return function () {throw name + " is not avaialble";};},
    base_paper = {
        init: function (placeholder) {},
        resize: function () {},
        import_file: not_implemented('import')
    };
//
$.lux.application('paper', {
    defaultElement: '<div>',
    renderers: {},
    defaults: {
        type: 'canvas'
    },
    add_paper_type: lux.app_method(function (name, r) {
        var engine = $.extend(true, {type: name}, base_paper, r);
        this.renderers[name] = function (elem) {
            var placeholder = $(elem),
                instance = $.extend({
                        container: function () {
                            return placeholder;
                        }
                    }, engine);
            return instance.init();
        };
    }),
    init: function () {
        var app = this.application(),
            paper = app.renderers[this.options.type];
        if (!paper) {
            throw 'unknwon paper ' + this.options.type;
        }
        this.renderer = paper(this.container());
    }
});