var TEST_REGEXP = /^\/base\/js\/tests\/specs\//i;
var allTestFiles = [];

// Get a list of all the test files to include
Object.keys(window.__karma__.files).forEach(function (file) {
    if (TEST_REGEXP.test(file)) {
        allTestFiles.push(file);
    }
});

require.config({
    // Karma serves files under /base, which is the basePath from your config file
    baseUrl: '/base/js',

    // dynamically load all test files
    deps: allTestFiles,

    // we have to kickoff jasmine, as it is asynchronous
    callback: function () {
        require(['angular', 'lux'], function (angular) {
            angular.module('$project_name', ['lux.loader', 'lux.restapi']);
            angular.bootstrap(document, ['$project_name']);
            window.__karma__.start();
        });
    }
});
