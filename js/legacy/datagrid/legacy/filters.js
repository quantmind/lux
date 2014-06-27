/**
 * Add individual column filtering
 */
datatable.extend('filters', {
    defaults: {
        string: 'input',
        range: {from: 'from', to: 'to'}
    },
    init: function () {
        var self = this;
        this.container().bind(self.after_method('setHeaders'), function () {
            self._build_filters();
        });
        this._super('init');
    },
    _build_filters: function () {
        var self = this,
            tr;
        $.each(this.data.headers.data, function (name, col) {
            // The column has filters
            if(col.filter) {
                if(!tr) {
                    tr = self._create_filter_row();
                }
                var elem = self['_' + col.filter + '_filter'](col).addClass('filter'),
                    th = tr.children('.' + self.prefixed('col-' + name));
                th.html('').append(elem);
            }
        });
    },
   // Range filter for numeric values
    _range_filter: function (col) {
        var options = this.options.filters,
            input1 = $(document.createElement('input')).attr({
                type: 'text',
                name: this._inputName(col.code + '__ge'),
                placeholder: options.range.from
            }),
            input2 = $(document.createElement('input')).attr({
                type: 'text',
                name: this._inputName(col.code + '__le'),
                placeholder: options.range.to
            });
        return $(document.createElement('div')).append(input1).append(input2).addClass('range');
    },
    _create_filter_row: function () {
        var self = this,
            tr = $(document.createElement('tr')).addClass('filters'),
            headers = this.data.headers;
        $.each(headers.codes, function (i, name) {
            tr.append($(document.createElement('th')).addClass(self.prefixed('col-' + name)));
        });
        return tr.appendTo(this._thead());
    }
    
});