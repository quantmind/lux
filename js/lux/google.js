
    //  Google Spreadsheet API
    //  -----------------------------
    //
    //  Create one by passing the key of the spreadsheeet containing data
    //
    //      var api = $lux.api({name: 'googlesheets', url: sheetkey});
    //
    lux.createApi('googlesheets', {
        //
        endpoint: "https://spreadsheets.google.com",
        //
        callback: function () {
            var feedsUrl = this.endpoint + '/feeds/worksheets/' + this.url + 'public/basic?alt=json';

        }
    };