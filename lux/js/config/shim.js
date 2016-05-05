define(function () {
    'use strict';
    // Default shim
    return function (root) {
        return {
            angular: {
                exports: 'angular'
            },
            'angular-strap-tpl': {
                deps: ['angular', 'angular-strap']
            },
            'google-analytics': {
                exports: root.GoogleAnalyticsObject || 'ga'
            },
            highlight: {
                exports: 'hljs'
            },
            'codemirror': {
                exports: 'CodeMirror'
            },
            'codemirror-htmlmixed': {
                deps: ['codemirror', 'codemirror-xml', 'codemirror-javascript', 'codemirror-css']
            },
            restangular: {
                deps: ['angular']
            },
            crossfilter: {
                exports: 'crossfilter'
            },
            trianglify: {
                deps: ['d3'],
                exports: 'Trianglify'
            },
            mathjax: {
                exports: 'MathJax'
            }
        };
    };

});
