(function () {
"use strict";

var d3physics = function (d3) {

    var physics = d3.layout.force().gravity(0).charge(0).friction(0),
        ontick = [],
        onstart = [],
        onend = [],
        event = d3.dispatch("start", "tick", "end"),
        dim = 1.0,
        quad,
        theta,
        theta2,
        dtime,
        currentTime,
        dt;

    physics.on('start', function (e) {
        var nodes = physics.nodes(),
            n = nodes.length,
            o,
            i;
        currentTime = new Date().getTime() * 0.001;
        // Set the velocity
        for (i = 0; i < n; ++i) {
            o = nodes[i];
            if (isNaN(o.vx)) o.vx = 0;
            if (isNaN(o.vy)) o.vy = 0;
        }
        for (i = 0; i < onstart.length; ++i)
            onstart[i](e);
        event.start(e);
    });

    physics.on('tick', function (e) {
        var nodes = physics.nodes(),
            n = nodes.length,
            o,
            i;

        quad = null;
        theta = physics.theta();
        theta2 = theta*theta;
        dt = dtime ? dtime : 0;
        if (!dt) {
            var newTime = new Date().getTime() * 0.001;
            dt = newTime - currentTime;
            currentTime = newTime;
        }
        for (i = 0; i < ontick.length; ++i)
            ontick[i](e);
        event.tick(e);
        //
        for (i = 0; i < n; ++i) {
            o = nodes[i];
            o.x += dt*o.vx;
            o.y += dt*o.vy;
        }
    });

    physics.on('end', function (e) {
        for (var i = 0; i < onend.length; ++i)
            onend[i](e);
        event.end(e);
    });

    function quadtree () {
        if (!quad)
            quad = d3.geom.quadtree(physics.nodes());
        return quad;
    }

    // Set the dt for each frame
    physics.dtime = function (x) {
        if (!arguments.length) return dtime;
        dtime = +x > 0 ? +x : 0;
        return physics;
    };

    physics.dim = function (x) {
        if (!arguments.length) return dim;
        dim = +x > 0 ? +x : 1.0;
        return physics;
    };
