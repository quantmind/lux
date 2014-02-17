
    module('lux.web.select');


    test("select", function() {
        equal(typeof(web.select), 'function', 'lux.web.dialog is an function');
        var s = web.select();
        equal(s.name, 'select');
        var element = s.element();
        equal(element.prop('tagName'), 'SELECT');
        require(['select'], function () {
            var select = s.select2();
            ok(select, 'select2 is available');
            test_destroy(s);
        });
    });
