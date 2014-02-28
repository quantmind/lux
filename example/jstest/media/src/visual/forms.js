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
