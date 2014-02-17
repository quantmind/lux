
    module('lux.web.dialog');

    test("dialog", function() {
        equal(typeof(web.dialog), 'function', 'lux.web.dialog is an function');
        var d = web.dialog({title: 'Hello World!'});
        equal(d.name, 'dialog');
        equal(d.buttons.children().length, 0, "No buttons");
        //
        // Closable
        ok(!d.options.closable, "dialog is not closable");
        d.closable();
        ok(d.options.closable, "dialog is closable");
        equal(d.buttons.children().length, 1, "One button");
        test_destroy(d);
    });

    //test("dialog.movable", function() {
    //    var d = web.dialog({title: 'I am movable', movable: true});
    //    equal(d.element().attr('draggable'), "true", 'Draggable attribute is true');
    //});