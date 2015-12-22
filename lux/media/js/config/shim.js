define([], function () {
    // Default shim
    return function (root) {
        return {
            angular: {
                exports: "angular"
            },
            "angular-strap-tpl": {
                deps: ["angular", "angular-strap"]
            },
            "angular-ui-select": {
                deps: ['angular']
            },
            "google-analytics": {
                exports: root.GoogleAnalyticsObject || "ga"
            },
            highlight: {
                exports: "hljs"
            },
            lux: {
                deps: ["angular", "lodash", "angular-file-upload"]
            },
            "ui-bootstrap": {
                deps: ["angular"]
            },
            "codemirror": {
                exports: "CodeMirror"
            },
            "codemirror-markdown": {
                deps: ["codemirror"]
            },
            "codemirror-xml": {
                deps: ["codemirror"]
            },
            "codemirror-javascript": {
                deps: ["codemirror"]
            },
            "codemirror-python": {
                deps: ["codemirror"]
            },
            "codemirror-css": {
                deps: ["codemirror"]
            },
            "codemirror-htmlmixed": {
                deps: ["codemirror", "codemirror-xml", "codemirror-javascript", "codemirror-css"],
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
    };

});
