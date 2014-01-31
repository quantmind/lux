//  Table view selections based on groups of columns.
//  It extends the datatable by adding
//      * a new `view` input in the layout object
//      * the `change_view` api function.
datatable.extend('views', {
    defaults: {
        groups: null,
    },
    layout: {
        views: function () {
            var self = this;
                groups = this.options.views.groups;
            if (!groups || groups.length === 0) {
                return;
            }
            var select = $(document.createElement('select')),
                initial = null,
                views = {};
            $.each(groups, function (i, group) {
                var cols = group.cols,
                    selector = cols.join(',.'),
                    opt;
                if (selector) {
                    opt = $("<option value='" + group.name + "'>" + group.display + "</option>");
                    views[group.name] = '.' + selector;
                    if (group.initial && !initial) {
                        initial = group.name;
                        opt.attr('selected', 'selected');
                    }
                    select.append(opt);
                }
            });
            this.data.views.select = select;
            this.data.views.groups = groups;
            //
            select.change(function () {
                self.change_view(this.value);
            });
            //
            return select;
        },
    },
    change_view: function () {
        if (value) {
            var cols = this.data.views.groups[value];
            if (cols) {
                var selected = [];
                $.each(this.data.headers.codes, function (i, code) {
                    if (cols.indexOf(code) !== -1) {
                        self._setColVisibility(code, true);
                    } else {
                        self._setColVisibility(code, false);
                    }
                });
                self.setHeaders(selected);
                self._rebuild_body();
            }
        }
    }
});