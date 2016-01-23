module.exports = function (config) {
    config.set({
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
        singleRun: true,
        files: [
            {pattern: 'js/build/lux/**/*.js', included: false},
            {pattern: 'js/tests/data/*.js', included: false},
            {pattern: 'js/tests/mocks/*.js', included: false},
            {pattern: 'js/tests/specs/sidebar/*.js', included: false},
            {pattern: 'js/build/tests.config.js'},
            {pattern: 'js/build/tests.runner.js'}
        ],
        reporters: ['coverage', 'dots', 'junit'],
        junitReporter: {
            outputDir: 'junit',
            outputFile: 'test-results.xml'
        }
    })
    ;
};
