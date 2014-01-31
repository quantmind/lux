/**
 * Subplots application manages a collection of plots of (possibly)
 * different types.
 */
var subplots = lux.application('subplots', {
    selector: '.subplot',
    defaultElement: '<div>',
    data: {
        plotters: {},
        all: [],
        byname: {},
        current: null
    },
    defaults: {
        default_plotter: null,
        // Draw when new data is set
        autodraw: true,
        layout: ['controls','plots'],
        plotLayout: 'tabs',
        series: {
            points: {
                show: false,
                radius: 3,
                lineWidth: 2, // in pixels
                fill: true,
                fillColor: "#ffffff",
                symbol: "circle" // or callback
            },
            lines: {
                // we don't put in show: false so we can see
                // whether lines were actively disabled
                lineWidth: 2, // in pixels
                fill: false,
                fillColor: null,
                steps: false
            },
            bars: {
                show: false,
                lineWidth: 2, // in pixels
                barWidth: 1, // in units of the x axis
                fill: true,
                fillColor: null,
                align: "left", // "left", "right", or "center"
                horizontal: false
            },
            shadowSize: 3,
            highlightColor: null
        }
    },
    plotType: function (name, plotter) {
        var self = this;
        plotter = $.extend(true, {}, {
            'name': name,
            defaults: {series: {}},
            draw: function (plot) {}
        }, plotter);
        if (self.defaults.default_plotter === null) {
            self.defaults.default_plotter = plotter.name;
        }
        self.data.plotters[name] = plotter;
    },
    /**
     * Called when initialising a new subplot instance
     */
    layout: function () {
        var self = this,
            container = self.container(),
            options = self.options;
        $.each(options.layout, function (i, name) {
            container.append($('<div>', {'class': name}));
        });
    },
    controlsContainer: function () {
        return this.container().find('.controls');
    },
    plotsContainer: function () {
        return this.container().find('.plots');
    },
    setData: function (data) {
        var self = this;
        self.clearData();
        self.addData(data);
    },
    clearData: function (plot) {
        var self = this;
        if(plot === undefined) {
            $.each(self.data.all, function (i, plot) {
                plot.destroy();
            });
            self.data.all = [];
            self.data.byname = {};
            self.data.current = null;
        }
    },
    addData: function (data) {
        var self = this,
            subplots = self.data,
            d;
        if (data) {
            // inspect the first element to check if this is a series of
            // subplots or data for a single canvas only
            d = data[0];
            if (d.series === undefined) {
                data = [{name: '', series: data}];
            }
            $.each(data, function (i, plot_data) {
                var name = plot_data.name || 'canvas' + (subplots.all.length + 1),
                    series = plot_data.series,
                    options = plot_data.options,
                    current = subplots.byname[name];
                if (current === undefined) {
                    current = self.create_plot(name, series, options);
                } else {
                    current.setData(series, options);
                }
                if (subplots.current === null) {
                    subplots.current = current;
                }
            });
            // Do we need to draw
            if (self.options.autodraw) {
                self.draw();
            }
        }
    },
    draw: function () {
        $.each(this.data.all, function (i, plot) {
            plot.draw();
        });
    },
    redraw: function () {
        $.each(this.data.all, function (i, plot) {
            plot.redraw();
        });
    },
    parseSeries: function (data) {
    },
    // Create a *new* plot instance for this subplots. This function
    // should not be invoked directly, but via the setdata/addData
    // API functions. You can however listen for events on it.
    create_plot: function (name, data_, options_) {
        var self = this,
            plotter = null,
            series = [],
            dirty = false,
            plot;
        //
        function update_data (data, options) {
            var old_data = [],
                old_plotter = plotter,
                plotter_name,
                base_serie;
            dirty = true;
            options = options || {};
            plotter_name = options.plotter || self.options.default_plotter;
            plotter = self.data.plotters[plotter_name];
            $.lux.utils.assert(plotter, "no plotter specified");
            base_serie = plotter.defaults.series;
            if (!!old_plotter && old_plotter.name === plotter.name) {
                old_data = series;
            }
            series = [];
            $.each(data, function (i, serie) {
                var s = $.extend(true, {}, base_serie);
                if (!!serie.data) {
                    s.data = serie.data; // move the data instead of deep-copy
                    delete serie.data;
                    $.extend(true, s, serie);
                    serie.data = s.data;
                } else {
                    s.data = serie;
                }
                series.push(s);
            });
        }
        //
        plot = {
            getName: function () {
                return name;
            },
            setData: function (data, options) {
                series = [];
                plotter = null;
                update_data(data, options);
            },
            updateData: update_data,
            getData: function () {
                return series;
            },
            getPlotter: function () {
                return plotter;
            },
            draw: function () {
                if(dirty) {
                    this.redraw();
                    dirty = false;
                }
            },
            redraw: function () {
                return plotter.draw(this);
            }
        };
        self.data.byname[name] = plot;
        self.data.all.push(plot);
        plot.updateData(data_, options_);
        return plot;
    }
});