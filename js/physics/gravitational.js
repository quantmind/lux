    // Gravitational forces

    var mass,
        // Big G - The Gravitational Constant in Newton*(m/kg)^2
        G = parseFloat('6.674e-11'),
        tiny = parseFloat('1e-9'),
        masses;

    // Earth mass and radius
    physics.EARTHMASS = parseFloat('5.97219e24');
    physics.EARTHRADIUS = 6371000;
    //
    // The small g (9.81) - gravity of earth is obtained via the 2nd law
    // g ~ G * EARTHMASS / (EARTHRADIUS*EARTHRADIUS)
    physics.mass = function (x) {
        if (!arguments.length) return mass;
        mass = typeof x === "function" ? x : +x;
        return physics;
    };

    onstart.push(function () {
        var nodes = physics.nodes(),
            n = nodes.length,
            m,
            i;
        masses = [];
        if (typeof mass === "function")
            for (i = 0; i < n; ++i) {
                m = +mass.call(physics, nodes[i], i);
                masses[i] = m > 0 ? m : tiny;
            }
        else {
            m = +mass > 0 ? +mass : tiny;
            for (i = 0; i < n; ++i)
                masses[i] = m;
        }
    });

    ontick.push(function (e) {
        var nodes = physics.nodes(),
            n = nodes.length,
            o,
            i;

        if (mass && dt) {
            quad = quadtree();
            centerOfMass(quad, e.alpha),
            i = -1;
            while (++i < n) {
                if (!(o = nodes[i]).fixed) {
                    quad.visit(gravitational(o, theta2, dt));
                }
            }
        }
    });

    // Apply gravitational force
    function gravitational (node, theta2, dt) {
        return function (quad, x1, _, x2) {
            if (quad.point !== node) {
                var dx = quad.cx - node.x,
                    dy = quad.cy - node.y,
                    dw = x2 - x1,
                    // distance
                    dn2 = dx * dx + dy * dy,
                    dn3 = dn2 * Math.sqrt(dn2),
                    dv;

                /* Barnes-Hut criterion. */
                if (dw * dw / theta2 < dn2) {
                    dv = dt * G * quad.mass / dn3;
                    node.vx += dv * dx;
                    node.vy += dv * dy;
                    return true;
                }

                if (quad.point && dn2) {
                    dv = dt * G * quad.pointMass / dn3;
                    node.vx += dv * dx;
                    node.vy += dv * dy;
                }
            }
            return !quad.mass;
        };
    }

    function centerOfMass (quad, alpha) {
        var cx = 0,
            cy = 0;
        quad.mass = 0;
        if (!quad.leaf) {
            var nodes = quad.nodes,
                n = nodes.length,
                i = -1,
                c;
            while (++i < n) {
                c = nodes[i];
                if (!c) continue;
                centerOfMass(c, alpha);
                quad.mass += c.mass;
                cx += c.mass * c.cx;
                cy += c.mass * c.cy;
            }
        }
        if (quad.point) {
            // jitter internal nodes that are coincident
            if (!quad.leaf) {
                quad.point.x += Math.random() - 0.5;
                quad.point.y += Math.random() - 0.5;
            }
            var k = masses[quad.point.index];
            quad.mass += quad.pointMass = k;
            cx += k * quad.point.x;
            cy += k * quad.point.y;
        }
        quad.cx = cx / quad.mass;
        quad.cy = cy / quad.mass;
    }
