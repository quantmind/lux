(function () {

    var root = this;
    var TEST_REGEXP = /\/js\/tests\/specs\//i;
    var allTestFiles = [];

    // Get a list of all the test files to include
    Object.keys(root.__karma__.files).forEach(function (file) {
        if (TEST_REGEXP.test(file)) {
            allTestFiles.push(file);
        }
    });


    root.lux = {
        //
        PATH_TO_LOCAL_REQUIRED_FILES: ${media_dir},
        //
        context: {
            API_URL: '/api',
            // Karma serves files under /base, which is the basePath from your config file
            MEDIA_URL: '/base/js'
        },
        //
        require: {
            //
            deps: allTestFiles,
            //
            callback: function () {
                root.__karma__.start();
            },
            //
            paths: ${require_paths}
        }
    };

}());
