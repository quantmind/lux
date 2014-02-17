
    var Cell = exports.Cell = lux.View.extend({
        tagName: "td",

        init: function (elem, options) {
            this._super(elem);
            this.column = options.column;
            if (!(this.column instanceof DataGridColumn)) {
                this.column = new DataGridColumn(this.column);
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