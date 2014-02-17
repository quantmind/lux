
    module('lux');

    test("lux", function() {
        equal(typeof(lux), 'object', 'Lux is an object');
        equal(typeof(lux.utils), 'object', 'lux.utils. is an object');
        //
        equal(typeof(lux.Ordered), 'function', 'Test Ordered collections');
        var o = new lux.Ordered();
        equal(o.size(), 0);
    });


    test("SkipList", function() {
        var sl = new lux.SkipList();
        equal(sl.length, 0, 'skiplist has 0 length');
        equal(sl.insert(4, 'ciao'), 1);
        equal(sl.insert(2, 'foo'), 2);
        equal(sl.insert(8, 'pippo'), 3);
        equal(sl.length, 3, 'skiplist has 3 elements');
        var r = [];
        sl.forEach(function (value) {
            r.push(value);
        });
        equal(r[0], 'foo', 'Correct first value');
        equal(r[1], 'ciao', 'Correct second value');
        equal(r[2], 'pippo', 'Correct third value');
    });