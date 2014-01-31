//
subplots.plotType('plot2d', {
    defaults: {
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
    draw: function (plot) {
        
    }
});
