module.exports = function(config) {

    var configuration = {

        browsers: ['PhantomJS', 'Firefox', 'Chrome'],

        phantomjsLauncher: {
            exitOnResourceError: true
        },
        basePath: '',
        frameworks: ['jasmine', 'browserify', 'es5-shim'],

        files: [
            'lux/js/tests/test-*.js'
        ],

        preprocessors: {
            'lux/js/**/*.js': 'browserify'
        },

        browserify: {
            //debug: true,
            transform: [
                ['babelify', {presets: ['es2015']}]
            ]
        },

        customLaunchers: {
            ChromeNoSandbox: {
                base: 'Chrome',
                flags: ['--no-sandbox']
            }
        }

        // define reporters, port, logLevel, browsers etc.
    };

    if(process.env.TRAVIS){
        configuration.browsers = ['PhantomJS', 'Firefox', 'ChromeNoSandbox'];
    }

    config.set(configuration);
};
