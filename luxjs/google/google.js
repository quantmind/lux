
    //  Google Spreadsheet API
    //  -----------------------------
    //
    //  Create one by passing the key of the spreadsheeet containing data
    //
    //      var api = $lux.api({name: 'googlesheets', url: sheetkey});
    //

    //
    //
    var GoogleModel = function ($lux, data, opts) {
        var i, j, ilen, jlen;
        this.column_names = [];
        this.name = data.feed.title.$t;
        this.elements = [];
        this.raw = data; // A copy of the sheet's raw data, for accessing minutiae

        if (typeof(data.feed.entry) === 'undefined') {
            $lux.log.warn("Missing data for " + this.name + ", make sure you didn't forget column headers");
            return;
        }

        $lux.log.info('Building models from google sheet');

        for (var key in data.feed.entry[0]) {
            if (/^gsx/.test(key)) this.column_names.push(key.replace("gsx$", ""));
        }

        for (i = 0, ilen = data.feed.entry.length; i < ilen; i++) {
            var source = data.feed.entry[i];
            var element = {};
            for (j = 0, jlen = this.column_names.length; j < jlen; j++) {
                var cell = source["gsx$" + this.column_names[j]];
                if (typeof(cell) !== 'undefined') {
                    if (cell.$t !== '' && !isNaN(cell.$t))
                        element[this.column_names[j]] = +cell.$t;
                    else
                        element[this.column_names[j]] = cell.$t;
                } else {
                    element[this.column_names[j]] = '';
                }
            }
            if (element.rowNumber === undefined)
                element.rowNumber = i + 1;
            this.elements.push(element);
        }
    };

    var GoogleSeries = function ($lux, data, opts) {
        var i, j, ilen, jlen;
        this.column_names = [];
        this.name = data.feed.title.$t;
        this.series = [];
        this.raw = data; // A copy of the sheet's raw data, for accessing minutiae

        if (typeof(data.feed.entry) === 'undefined') {
            $lux.log.warn("Missing data for " + this.name + ", make sure you didn't forget column headers");
            return;
        }
        $lux.log.info('Building series from google sheet');

        for (var key in data.feed.entry[0]) {
            if (/^gsx/.test(key)) {
                var name = key.replace("gsx$", "");
                this.column_names.push(name);
                this.series.push([name]);
            }
        }

        for (i = 0, ilen = data.feed.entry.length; i < ilen; i++) {
            var source = data.feed.entry[i];
            for (j = 0, jlen = this.column_names.length; j < jlen; j++) {
                var cell = source["gsx$" + this.column_names[j]],
                    serie = this.series[j];
                if (typeof(cell) !== 'undefined') {
                    if (cell.$t !== '' && !isNaN(cell.$t))
                        serie.push(+cell.$t);
                    else
                        serie.push(cell.$t);
                } else {
                    serie.push('');
                }
            }
        }
    };
