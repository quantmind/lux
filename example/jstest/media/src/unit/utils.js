//
//  Test utility functions
//
module('lux.utils');

test("allClasses", function() {
    var allClasses = lux.utils.allClasses,
        el = $('<div>');
    ok(_.isArray(allClasses(el)));
    equal(allClasses(el).length, 0);
    el.addClass('bla foo');
    var cs = allClasses(el);
    equal(cs.length, 2);
});

test("urljoin", function () {
    var urljoin = lux.utils.urljoin;
    equal(urljoin('bla', 'foo'), 'bla/foo', 'Got bla/foo');
    equal(urljoin('bla/', '//foo.com', '', '//', 'pippo'),
            'bla/foo.com/pippo', 'Got bla/foo.com/pippo');
    equal(urljoin('http://bla/', '//foo.com', '', '//', 'pippo'),
            'http://bla/foo.com/pippo', 'Got http://bla/foo.com/pippo');
});
