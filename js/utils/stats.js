//
var random = Math.random,
    log = Math.log,
    NV_MAGICCONST = 4 * Math.exp(-0.5)/Math.sqrt(2.0);
//
$.extend(math, {
    //
    // Normal variates using the ratio of uniform deviates algorithm
    normalvariate: function (mu, sigma) {
        var u1, u2, z, zz; 
        while (true) {
            u1 = random();
            u2 = 1.0 - random();
            z = NV_MAGICCONST*(u1-0.5)/u2;
            zz = z*z/4.0;
            if (zz <= -log(u2)) {
                break;
            }
        }
        return mu + z*sigma;
    }
});