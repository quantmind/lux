
    //
    return lux.createView('VisualTest', {
        //
        selector: '.visual-test',
        //
        initialise: function (options) {
            var test = visual_map[options.test];
            if (test) {
                this.tests = [options.test];
            } else {
                this.tests = visual_tests;
            }
        },
        //
        render: function () {
            var elem = this.elem.empty(),
                tests = this.tests,
                grid = new lux.Grid({rows: [[18, 6]]}),
                row = grid.elem.children().first(),
                cols = row.children(),
                col1 = cols[0],
                col2 = cols[1];
            elem.append(grid.elem);
            //
            _(tests).forEach(function (name) {
                var callable = visual_map[name],
                    view = new VisualTest({
                        render: callable,
                        'elem': col1
                    });
                view.text('h2', name);
                view.render();
            });
        }
    });
    //
});
