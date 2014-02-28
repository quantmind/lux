define(['lux', 'lorem'], function (lux, lorem) {
    //
    var
    //
    visual_tests = [],
    //
    visual_map = {},
    //
    VisualTest = lux.View.extend({

        initialise: function (options) {
            var self = this;
            this.render = function () {
                options.render.call(self, self);
            };
        },

        text: function(tag, text) {
            this.elem.append($(document.createElement(tag)).html(text));
        },

        // Create an example box and append ``elem``
        example: function (elem) {
            var el = $(document.createElement('div')).addClass(
                'lux-example default').append(elem);
            this.elem.append(el);
        }
    }),
    //
    visualTest = function (name, callable) {
        visual_map[name] = callable;
        visual_tests.push(name);
    };

    // Forms
    visualTest('Forms', function (self) {
        //
        var
        //
        fields = [
            new lux.Field('email', {
                label: 'Email address',
                type: 'email',
                autocomplete: 'off'
            }),
            new lux.Field('password', {
                type: 'password',
                autocomplete: 'off',
                placeholder: 'Type your password'
            }),
            new lux.BooleanField('remember', {
                label: 'Remember me'
            }),
            new lux.ChoiceField('choices', {
                choices: ['blue', 'black', 'red'],
                select2: {minimumResultsForSearch: -1},
                label: false
            })
        ];

        self.text('h3', 'Default forms');
        self.text('p', 'Forms can have the <code>default</code> or <code>.inverse</code> classes.');

        var form = new lux.Form();
        self.example(form.elem.addClass('span12'));
        form.addFields(fields);
        form.addSubmit();
        form.render();

        //self.example(form.elem.addClass('span12'));
        //
        //form = new lux.Form({skin: 'inverse'});
        //form.addFields(fields);
        //form.addSubmit();
        //form.render();
        //self.example(form.elem);
        var inlineFields = _.filter(fields, function (field) {
            return field.name !== 'choices';
        });
        self.text('h3', 'Inline forms');
        form = new lux.Form({layout: 'inline'});
        self.example(form.elem);
        form.addFields(inlineFields);
        form.addSubmit();
        form.render();

    });

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
