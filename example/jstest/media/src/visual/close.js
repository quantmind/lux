
    //
    return lux.createView('VisualTest', {
        //
        selector: '.visual-test',
        //
        initialise: function (options) {
            var test = web.visual_tests[options.test];
            if (test) {
                this.tests = [test];
            } else {
                this.tests = lux.web.visual_tests;
            }
        },
        //
        render: function () {
            var elem = this.elem.empty();
            _(this.tests).forEach(function (test) {
                test.call(elem);
            });
        }
    });
    //
});
