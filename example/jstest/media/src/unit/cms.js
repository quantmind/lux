module('lux.cms');

test("Content", function() {
    var cms = lux.cms,
        Content = cms.Content;
    equal(Content._meta.name, 'content', 'Content meta name is content');
    Content._meta.set_transport(new lux.Storage({type: 'session'}));
    equal(Content._meta._backend.storage, sessionStorage, 'Backend on sessionStorage');
    //
    // Test Views
    var RowView = cms.RowView;
    var row = new RowView();
    ok(row instanceof cms.ContentView, 'Testing RowView class');
});