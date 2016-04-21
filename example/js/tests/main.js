(function () {
    'use strict';

    // Create the tests runner bundle
    var tests = [];

    // Get a list of all the test files to include
    Object.keys(window.__karma__.files).forEach(function (file) {
        if (/test_.*.js$/i.test(file)) {
            tests.push(file);
        }
    });

    require.config({
        baseUrl: '/base',
        deps: ['require.config'],
        callback: function () {
            require.config({
                deps: tests,
                callback: window.__karma__.start
            });
        }
    });
}());
