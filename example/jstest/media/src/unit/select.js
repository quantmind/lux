module('lux.web.select');


test("select", function() {
    equal(typeof(web.select), 'function', 'lux.web.dialog is an function');
    var s = web.select();
    equal(s.name, 'select');
    var element = s.element();
    equal(element.prop('tagName'), 'SELECT');
    var select2 = s.select2();
    var container = s.container();
    ok(element[0] !== container[0], "Different container");
    test_destroy(s);
});
