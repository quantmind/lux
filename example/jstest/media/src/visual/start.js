define(['lux', 'lorem'], function (lux, lorem) {
    //
    var
    //
    visual_tests = [],
    //
    visual_map = {},
    //
    VisualTest = lux.View.extend({

        initialise: function (options) {
            var self = this;
            this.render = function () {
                options.render.call(self, self);
            };
        },

        text: function(tag, text) {
            this.elem.append($(document.createElement(tag)).html(text));
        },

        // Create an example box and append ``elem``
        example: function (elem) {
            var el = $(document.createElement('div')).addClass(
                'lux-example default').append(elem);
            this.elem.append(el);
        }
    }),
    //
    visualTest = function (name, callable) {
        visual_map[name] = callable;
        visual_tests.push(name);
    };
