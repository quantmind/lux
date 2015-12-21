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
        },{
            pattern: 'luxsite/media/js/**/*.js',
            included: false
        },{
            pattern: 'luxsite/build/**/*.js',
            included: false
        },
            'luxsite/media/build/test.config.js',
            'luxsite/media/js/app.js'
        ],
        reporters: ['coverage', 'dots', 'junit'],
        junitReporter: {
            outputDir: 'junit',
            outputFile: 'test-results.xml'
        }
    })
    ;
};
