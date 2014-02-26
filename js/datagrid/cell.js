
    var Cell = exports.Cell = lux.createView('datagridcell', {
        tagName: "td",

        initialise: function (options) {
            var model = this.model;
            this.column = options.column;
            if (!(this.column instanceof DataGridColumn)) {
                this.column = new DataGridColumn(this.column);
            }
            if (model) {
                var value = model.get(this.column.id());
                if (value)
                    this.elem.html(value);
            }
        },

        exitEditMode: function () {
            this.elem.removeClass("error");
            this.currentEditor.remove();
            this.stopListening(this.currentEditor);
            delete this.currentEditor;
            this.elem.removeClass("editor");
            this.render();
        }

    });