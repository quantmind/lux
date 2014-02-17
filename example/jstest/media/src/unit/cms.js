
    module('lux.cms');

    test("cms", function () {
        equal(cms, lux.cms);
        ok(cms.views, 'views object');
    });

    test("Content", function() {
        var Content = cms.Content;
        equal(Content._meta.name, 'content', 'Content meta name is content');
        //
        // Test Views
        var row = new cms.views.row();
        ok(row instanceof cms.views.row, 'Testing RowView class');
    });
