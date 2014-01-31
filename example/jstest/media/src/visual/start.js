define(['jquery', 'lux-web'], function ($) {
    //
    var each = lux.each;
    //
    lux.web.visual_tests = {};
    lux.web.visual_test = function (test, callable) {
        lux.web.visual_tests[test] = callable;
    };
    //
    lux.web.extension('visual_test', {
        selector: 'div.visual-test',
        decorate: function () {
            var test = lux.web.visual_tests[this.options.test];
            if (test) {
                var grid = lux.web.grid(this.element(), {template: '75-25'}),
                    //logger = $(document.createElement('div')).height(500),
                    panel = $(document.createElement('div')),
                    columns = grid.element().children();
                panel.appendTo(columns[0]);
                //logger.appendTo(columns[1]);
                //lux.web.logger.addElement(logger);
                test.call(panel);
            }
        }
    });
    //