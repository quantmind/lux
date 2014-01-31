var math = {},
    PI = Math.PI;
//
lux.math = math;
//
$.extend(math, {
    point2d: function (x, y) {
        return {'x': x, 'y': y};
    },
    distance2d: function (p1, p2) {
        return Math.sqrt(((p1.x - p2.x) * (p1.x - p2.x)) +
                         ((p1.y - p2.y) * (p1.y - p2.y)));
    },
    // angle (in radians) between 3 points
    //        x3,y3
    //       /
    //   x2,y2
    //       \
    //       x1,y1
    angle2d: function (x1, y1, x2, y2, x3, y3) {
        var xx1 = x1-x2,
            yy1 = y1-y2,
            xx2 = x3-x2,
            yy2 = y3-y2,
            a1 = Math.atan2(xx1, yy1),
            a2 = Math.atan2(xx2, yy2);
        return a1 - a2;
    },
    degree: function (rad) {
        return 180 * rad / PI;
    },
    radians: function (deg) {
        return PI * deg / 180;
    }
});
