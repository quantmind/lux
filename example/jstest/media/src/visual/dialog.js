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

        //
        self.text('h3', 'Modal dialog');
        var
        open = new lux.Button({
            text: 'Click to pen model dialog',
        }),
        modal = new lux.Dialog({
            modal: true,
            title: 'A modal dialog',
            body: lorem({words: 20}),
            autoOpen: false
        });
        self.example(open.elem.click(function () {
            modal.render();
        }));
    });