// Server side data
datatable.extend('server', {
    defaults: {
        source: null
    },
    sort: function (head) {
        if(!this.options.server.source) {
            return this._super('sort', head);
        } else {
            
        }
    }
});