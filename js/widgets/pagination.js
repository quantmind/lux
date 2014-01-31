
$.lux.application('pagination', {
    selector: '.pagination',
    defaultElement: '<div>',
    defaults: {
        type: 'numbers', // either "numbers" or "simple"
        length: 25, // number of rows to display
        start: 0,   // the start element
        numbers: {
            first: "first",
            previous: "previous",
            next: "next",
            last: "last"
        }    
    },
    init: function () {
        var ul = $(document.createElement('ul')),
            type = this.options.pagination.type;
            func = this['_paginate_' + type];
        func.apply(this);
    }
});