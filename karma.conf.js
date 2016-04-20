module.exports = function (config) {

    var configuration = {

        frameworks: ['jasmine', 'requirejs', 'es5-shim'],

        browsers: ['PhantomJS', 'Chrome', 'Firefox'],

        preprocessors: {
            'js/!(build|tests|deps)/**/!(templates).js': ['coverage']
        },

        coverageReporter: {
            includeAllSources: true,
            reporters: [{
                type: 'html',
                dir: 'coverage/'
            }, {
                type: 'lcovonly',
                dir: 'coverage/'
            }, {
                type: 'cobertura',
                dir: 'coverage/'
            },{
                type: 'text-summary'
            }],
            subdir: function (browser) {
                return browser.toLowerCase().split(/[ /-]/)[0];
            }
        },

        basePath: 'example/js',

        files: [
            {pattern: 'lux/**/*.js', included: false},
            {pattern: '*.js', included: false},
            {pattern: 'tests/data/*.js', included: false},
            {pattern: 'tests/mocks/*.js', included: false},
            {pattern: 'tests/test_*.js', included: false},
            'tests/main.js',
        ],

        reporters: ['coverage', 'dots', 'junit'],

        junitReporter: {
            outputDir: 'junit',
            outputFile: 'test-results.xml'
        },
        
        customLaunchers: {
            ChromeNoSandbox: {
                base: 'Chrome',
                flags: ['--no-sandbox']
            }
        }
    };

    if (process.env.TRAVIS){
        configuration.browsers = ['PhantomJS', 'Firefox', 'ChromeNoSandbox'];
    }

    config.set(configuration);
};
