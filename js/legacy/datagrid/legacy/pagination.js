// Table pagination
datatable.extend('pagination', {
    defaults: {
        type: 'numbers', // either "numbers" or "simple"
        length: 25, // number of rows to display
        start: 0,    // the start element
        numbers: {
            first: "first",
            previous: "previous",
            next: "next",
            last: "last"
        }    
    },
    layout: {
        pagination: function () {
            var pag = $(document.createElement('div'));
            if(this.options.pagination.type === 'numbers') {
                this._paginate_numbers(pag);
            } else if(this.options.pagination.type === 'simple') {
                this._paginate_simple(pag);
            }
            if(pag.length) {
                return pag;
            }
        }
    },
    _paginate_numbers: function (pagination) {
        var numbers = this.options.pagination.numbers,
            nFirst = $(document.createElement('span')).html(numbers.first),
            nPrevious = $(document.createElement('span')).html(numbers.previous),
            nList = $(document.createElement('span')),
            nNext = $(document.createElement('span').html(numbers.next)),
            nLast = $(document.createElement('span').html(numbers.last));
        pagination.append(nFirst).append(nPrevious).append(nList).append(nNext).append(nLast);
    }
});