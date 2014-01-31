// Search box for global table search
datatable.extend('search', {
    layout: {
        search: '<input name="sSearch" placeholder="search">'
    },
    init: function () {
        var self = this,
            options = this.options,
            sPreviousSearch = null,
            oTimerId = null,
            input;
        this._super('init');
        input = this.container().find('input[name="sSearch"]');
        input.unbind('keyup').bind('keyup', function () {
            if (sPreviousSearch === null || sPreviousSearch !== input.val()) {
                window.clearTimeout(oTimerId);
                sPreviousSearch = input.val();
                oTimerId = window.setTimeout(function () {
                    self.search(input.val());
                }, options.inputs.delay);
            }
        });
    },
    search: function () {
        
    }
});