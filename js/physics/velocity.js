    //
    //  VELOCITY FIELD
    //  -------------------

    // Handle velocity fields
    //
    var velocity;

    // Add a velocity field, can be a function or a two element array
    physics.velocityField = function (x) {
        if (!arguments.length) return velocity;
        velocity = x;
        return physics;
    };

    ontick.push(function (e) {
        if (velocity) {
            var nodes = physics.nodes(),
                n = nodes.length,
                i;
            if (typeof velocity === 'function') {
                var vel;
                for (i = 0; i < n; ++i) {
                    vel = velocity.call(physics, nodes[i]);
                    nodes[i].px += vel[0]*dt;
                    nodes[i].py += vel[1]*dt;
                }
            } else
                for (i = 0; i < n; ++i) {
                    nodes[i].px += velocity[0]*dt;
                    nodes[i].px += velocity[1]*dt;
                }
        }
    });
    //