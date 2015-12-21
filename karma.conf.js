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
        files: [{
            pattern: 'lux/media/js/**/*.js',
            included: false
        }, {
            pattern: 'js/**/*.js',
            included: false
        },
            'luxsite/media/js/test.config.js',
            'js/require.config.js',
            'js/tests/karma.main.js'
        ],
        reporters: ['coverage', 'dots', 'junit'],
        junitReporter: {
            outputDir: 'junit',
            outputFile: 'test-results.xml'
        }
    })
    ;
};
