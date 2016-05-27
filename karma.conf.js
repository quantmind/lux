module.exports = function(config) {

    var configuration = {

        browsers: ['PhantomJS', 'Firefox', 'Chrome'],

        phantomjsLauncher: {
            exitOnResourceError: true
        },
        basePath: '',
        frameworks: ['jasmine', 'browserify', 'es5-shim'],

        files: [
            'lux/js/cms/*.js',
            'lux/js/core/*.js',
            'lux/js/form/*.js',
            'lux/js/grid/*.js',
            'lux/js/lux/*.js',
            'lux/js/nav/*.js',
            'lux/js/tests/*.js'
        ],

        preprocessors: {
            'lux/js/**/*.js': ['browserify']
        },

        // coverage reporter generates the coverage
        reporters: ['progress', 'coverage'],

        browserify: {
            debug: true,
            transform: [
                [
                    'babelify',
                    {
                        presets: ['es2015']
                    }
                ]
                //[
                //    'browserify-istanbul',
                //    {
                //        instrumenterConfig: {
                //            embedSource: true
                //        }
                //    }
                //]
            ]
        },

        customLaunchers: {
            ChromeNoSandbox: {
                base: 'Chrome',
                flags: ['--no-sandbox']
            }
        },

        // optionally, configure the reporter
        coverageReporter: {
            type : 'html',
            dir : 'coverage/'
        }

        // define reporters, port, logLevel, browsers etc.
    };

    if(process.env.TRAVIS){
        configuration.browsers = ['PhantomJS', 'Firefox', 'ChromeNoSandbox'];
    }

    config.set(configuration);
};
