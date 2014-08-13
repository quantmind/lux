    //
    lux.d3plugins = {};

    var Viz = lux.Viz,
        //
        Chernoff = lux.d3plugins.Chernoff = Viz.extend({
            d3build: function (d3) {
                var face = this.attrs.face,
                    stroke = this.attrs.stroke || '#000',
                    c = d3.chernoff()
                            .face(function(d) { return d.f; })
                            .hair(function(d) { return d.h; })
                            .mouth(function(d) { return d.m; })
                            .nosew(function(d) { return d.nw; })
                            .noseh(function(d) { return d.nh; })
                            .eyew(function(d) { return d.ew; })
                            .eyeh(function(d) { return d.eh; })
                            .brow(function(d) { return d.b; }),
                    svg = this.svg(d3);

                if (face) {
                    face = lux.$.parseJSON(face);
                    if (face.constructor !== Array) face = [face];
                }

                svg.selectAll("g.chernoff").data(face).enter()
                        .append("svg:g")
                        .attr("class", "chernoff").attr('stroke', stroke).attr('fill', 'none')
                        .attr("transform", function(d, i) {
                            return "scale(1." + i + ")translate(" +
                                (i*100) + "," + (i*100) + ")";
                        }).call(c);
            }
        });

    lux.app.directive('chernoff', lux.vizDirectiveFactory(Chernoff));

});