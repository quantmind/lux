    return d3.rebind(physics, event, "on");
};

if (typeof define === "function" && define.amd)
    define(function () {return d3physics;});
else if (typeof module === "object" && module.exports)
    module.exports = d3physics;
else
    window.d3physics = d3physics;

}());