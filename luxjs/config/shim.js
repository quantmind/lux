
    // Default shims
    function defaultShim () {
        return {
            angular: {
                exports: "angular"
            },
            "google-analytics": {
                exports: root.GoogleAnalyticsObject || "ga"
            },
            highlight: {
                exports: "hljs"
            },
            lux: {
                deps: ["angular"]
            },
            restangular: {
                deps: ["angular"]
            },
            crossfilter: {
                exports: "crossfilter"
            },
            trianglify: {
                deps: ["d3"],
                exports: "Trianglify"
            },
            mathjax: {
                exports: "MathJax"
            }
        };
    }