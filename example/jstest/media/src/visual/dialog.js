    //
    //  Dialog visual tests
    //  -----------------------------
    //
    visualTest('Dialog', function (self) {
        //
        self.text('h3', 'Basic usage');
        //
        var
        dialog = new lux.Dialog({
            title: 'A simple dialog',
            body: lorem({words: 20}),
            width: 400
        });
        self.example(dialog.elem);

        var elem = $('<div></div>');
        self.example(elem);
        elem.dialog({
            title: 'A dialog with buttons',
            body: lorem({words: 20}),
            width: 400,
            skin: 'primary',
            closable: true,
            collapsable: true,
            fullscreen: true
        });
    });