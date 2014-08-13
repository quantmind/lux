define(['lux'], function (lux) {
(function() {
function sign(num) {
    if(num > 0) {
        return 1;
    } else if(num < 0) {
        return -1;
    } else {
        return 0;
    }
}

// Implements Chernoff faces (http://en.wikipedia.org/wiki/Chernoff_face).
// Exposes 8 parameters through functons to control the facial expression.
// face -- shape of the face {0..1}
// hair -- shape of the hair {-1..1}
// mouth -- shape of the mouth {-1..1}
// noseh -- height of the nose {0..1}
// nosew -- width of the nose {0..1}
// eyeh -- height of the eyes {0..1}
// eyew -- width of the eyes {0..1}
// brow -- slant of the brows {-1..1}
function d3_chernoff() {
    var facef = 0.5, // 0 - 1
        hairf = 0, // -1 - 1
        mouthf = 0, // -1 - 1
        nosehf = 0.5, // 0 - 1
        nosewf = 0.5, // 0 - 1
        eyehf = 0.5, // 0 - 1
        eyewf = 0.5, // 0 - 1
        browf = 0, // -1 - 1

        line = d3.svg.line()
            .interpolate("cardinal-closed")
            .x(function(d) { return d.x; })
            .y(function(d) { return d.y; }),
        bline = d3.svg.line()
            .interpolate("basis-closed")
            .x(function(d) { return d.x; })
            .y(function(d) { return d.y; });

    function chernoff(a) {
        if(a instanceof Array) {
            a.each(__chernoff);
        } else {
            d3.select(this).each(__chernoff);
        }
    }

    function __chernoff(d) {
        var ele = d3.select(this),
            facevar = (typeof(facef) === "function" ? facef(d) : facef) * 30,
            hairvar = (typeof(hairf) === "function" ? hairf(d) : hairf) * 80,
            mouthvar = (typeof(mouthf) === "function" ? mouthf(d) : mouthf) * 7,
            nosehvar = (typeof(nosehf) === "function" ? nosehf(d) : nosehf) * 10,
            nosewvar = (typeof(nosewf) === "function" ? nosewf(d) : nosewf) * 10,
            eyehvar = (typeof(eyehf) === "function" ? eyehf(d) : eyehf) * 10,
            eyewvar = (typeof(eyewf) === "function" ? eyewf(d) : eyewf) * 10,
            browvar = (typeof(browf) === "function" ? browf(d) : browf) * 3;

        var face = [{x: 70, y: 60}, {x: 120, y: 80},
                    {x: 120-facevar, y: 110}, {x: 120-facevar, y: 160},
                    {x: 20+facevar, y: 160}, {x: 20+facevar, y: 110},
                    {x: 20, y: 80}];
        ele.selectAll("path.face").data([face]).enter()
            .append("path")
            .attr("class", "face")
            .attr("d", bline);

        var hair = [{x: 70, y: 60}, {x: 120, y: 80},
                    {x: 140, y: 45-hairvar}, {x: 120, y: 45},
                    {x: 70, y: 30}, {x: 20, y: 45},
                    {x: 0, y: 45-hairvar}, {x: 20, y: 80}];
        ele.selectAll("path.hair").data([hair]).enter()
            .append("path")
            .attr("class", "hair")
            .attr("d", bline);

        var mouth = [{x: 70, y: 130+mouthvar},
                     {x: 110-facevar, y: 135-mouthvar},
                     {x: 70, y: 140+mouthvar},
                     {x: 30+facevar, y: 135-mouthvar}];
        ele.selectAll("path.mouth").data([mouth]).enter()
            .append("path")
            .attr("class", "mouth")
            .attr("d", line);

        var nose = [{x: 70, y: 110-nosehvar},
                    {x: 70+nosewvar, y: 110+nosehvar},
                    {x: 70-nosewvar, y: 110+nosehvar}];
        ele.selectAll("path.nose").data([nose]).enter()
            .append("path")
            .attr("class", "nose")
            .attr("d", line);

        var leye = [{x: 55, y: 90-eyehvar}, {x: 55+eyewvar, y: 90},
                    {x: 55, y: 90+eyehvar}, {x: 55-eyewvar, y: 90}];
        var reye = [{x: 85, y: 90-eyehvar}, {x: 85+eyewvar, y: 90},
                    {x: 85, y: 90+eyehvar}, {x: 85-eyewvar, y: 90}];
        ele.selectAll("path.leye").data([leye]).enter()
            .append("path")
            .attr("class", "leye")
            .attr("d", bline);
        ele.selectAll("path.reye").data([reye]).enter()
            .append("path")
            .attr("class", "reye")
            .attr("d", bline);

        ele.append("path")
            .attr("class", "lbrow")
            .attr("d", "M" + (55-eyewvar/1.7-sign(browvar)) + "," +
                       (87-eyehvar+browvar) + " " +
                       (55+eyewvar/1.7-sign(browvar)) + "," +
                       (87-eyehvar-browvar));
        ele.append("path")
            .attr("class", "rbrow")
            .attr("d", "M" + (85-eyewvar/1.7+sign(browvar)) + "," +
                       (87-eyehvar-browvar) + " " +
                       (85+eyewvar/1.7+sign(browvar)) + "," +
                       (87-eyehvar+browvar));
    }

    chernoff.face = function(x) {
        if(!arguments.length) return facef;
        facef = x;
        return chernoff;
    };

    chernoff.hair = function(x) {
        if(!arguments.length) return hairf;
        hairf = x;
        return chernoff;
    };

    chernoff.mouth = function(x) {
        if(!arguments.length) return mouthf;
        mouthf = x;
        return chernoff;
    };

    chernoff.noseh = function(x) {
        if(!arguments.length) return nosehf;
        nosehf = x;
        return chernoff;
    };

    chernoff.nosew = function(x) {
        if(!arguments.length) return nosewf;
        nosewf = x;
        return chernoff;
    };

    chernoff.eyeh = function(x) {
        if(!arguments.length) return eyehf;
        eyehf = x;
        return chernoff;
    };

    chernoff.eyew = function(x) {
        if(!arguments.length) return eyewf;
        eyewf = x;
        return chernoff;
    };

    chernoff.brow = function(x) {
        if(!arguments.length) return browf;
        browf = x;
        return chernoff;
    };

    return chernoff;
}

d3.chernoff = function() {
    return d3_chernoff(Object);
};
})();
(function() {
  d3.force_labels = function force_labels() {
    var labels = d3.layout.force();

    // Update the position of the anchor based on the center of bounding box
    function updateAnchor() {
      if (!labels.selection) return;
      labels.selection.each(function(d) {
        var bbox = this.getBBox(),
            x = bbox.x + bbox.width / 2,
            y = bbox.y + bbox.height / 2;

        d.anchorPos.x = x;
        d.anchorPos.y = y;

        // If a label position does not exist, set it to be the anchor position
        if (d.labelPos.x === null) {
          d.labelPos.x = x;
          d.labelPos.y = y;
        }
      });
    }

    //The anchor position should be updated on each tick
    labels.on("tick.labels", updateAnchor);

    // This updates all nodes/links - retaining any previous labelPos on updated nodes
    labels.update = function(selection) {
      labels.selection = selection;
      var nodes = [], links = [];
      selection[0].forEach(function(d) {
        if(d && d.__data__) {
          var data = d.__data__;

          if (!d.labelPos) d.labelPos = {fixed: false};
          if (!d.anchorPos) d.anchorPos = {fixed: true};

          // Place position objects in __data__ to make them available through
          // d.labelPos/d.anchorPos for different elements
          data.labelPos = d.labelPos;
          data.anchorPos = d.anchorPos;

          links.push({target: d.anchorPos, source: d.labelPos});
          nodes.push(d.anchorPos);
          nodes.push(d.labelPos);
        }
      });
      labels
          .stop()
          .nodes(nodes)
          .links(links);
      updateAnchor();
      labels.start();
    };
    return labels;
  };
})();
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