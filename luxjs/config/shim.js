
    // Default shims
    function defaultShim () {
        return {
            angular: {
                exports: "angular"
            },
            "angular-strap-tpl": {
                deps: ["angular", "angular-strap"]
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
            "ui-bootstrap": {
                deps: ["angular"]
            },
            "codemirror-markdown": {
                deps: ["codemirror"],
                exports: "CodeMirror"
            },
            "codemirror-htmlmixed": {
                deps: ["codemirror", "codemirror-xml", "codemirror-javascript", "codemirror-css"],
                exports: "CodeMirror"
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
