(function () {

    var TEST_REGEXP = /\/tests\/specs\//i;
    var allTestFiles = [];

    // Get a list of all the test files to include
    Object.keys(window.__karma__.files).forEach(function (file) {
        if (TEST_REGEXP.test(file)) {
            allTestFiles.push(file);
        }
    });


    window.lux = {
        //
        PATH_TO_LOCAL_REQUIRED_FILES: '${media_dir}',
        //
        context: {
            API_URL: '/api',
            // Karma serves files under /base, which is the basePath from your config file
            MEDIA_URL: '/base/tests'
        },
        //
        require: {
            //
            deps: allTestFiles,
            //
            callback: function () {
                window.__karma__.start();
            }
        }
    };

    //window.lux.require.paths = ${require_paths};

}());
