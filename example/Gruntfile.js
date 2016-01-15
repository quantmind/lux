/*eslint-env node */
module.exports = function(grunt) {
    'use strict';
    // bmll configuration.
    var config_file = 'js/config.json',
        cfg = grunt.file.readJSON(config_file),
        jslibs = cfg.js,
        path = require('path'),
        _ = require('lodash'),
        baseTasks = ['shell:buildLuxConfig', 'luxbuild'],
        jsTasks = ['requirejs'],
        cssTasks = [],
        // These entries are tasks configurators not libraries
        skipEntries = ['options', 'watch'],
        concats = {
            options: {
                sourceMap: false // TODO change to true when Chrome sourcemaps bug is fixed
            }
        },
        requireOptions = {
            baseUrl: 'js/',
            generateSourceMaps: false, // TODO change to true when Chrome sourcemaps bug is fixed
            optimize: 'none',
            paths: {
                angular: 'empty:',
                lux: 'empty:',
                d3: 'empty:',
                'angular-cookies': 'empty:',
                'angular-strap': 'empty:',
                'angular-file-upload': 'empty:',
                'angular-img-crop': 'empty:',
                'moment': 'empty:',
                'angular-moment': 'empty:',
                'angular-sanitize': 'empty:',
                'angular-ui-grid': 'empty:',
                'angular-infinite-scroll': 'empty:',
                'videojs': 'empty:',
                'giotto': 'empty:',
                'angular-touch': 'empty:', // TODO this is a lux dependency, should be removed
                'angular-scroll': 'empty:', // TODO find out who is using this
                'angular-ui-select': 'empty:', // TODO find out who is using this
                'angular-ui-router': 'empty:',
                'angular-strap-tpl': 'empty:',
                'moment-timezone': 'empty:',
                'lodash': 'empty:'
            },
            name: 'app',
            out: 'js/build/bundle.js'
        };

    if (!jslibs) {
        grunt.log.error('"js" entry not available in "' + config_file + '"');
        return grunt.failed;
    }

    delete cfg.js;

    cfg.pkg = grunt.file.readJSON('package.json');
    cfg.requirejs = {
        compile: {
            options: _.extend({
                name: 'app',
                out: 'js/build/bundle.js'
            }, requireOptions)
        },
        tests: {
            options: _.extend({
                name: 'tests/runner',
                out: 'js/build/tests.runner.js'
            }, requireOptions)
        }
    };
    cfg.concat = concats;

    // Tasks run by lux python library
    cfg.shell = {
        buildLuxConfig: {
            options: {
                stdout: true,
                stderr: true
            },
            command: function() {
                return path.resolve('manage.py') + ' media';
            }
        },
        buildPythonCSS: {
            options: {
                stdout: true,
                stderr: true
            },
            command: function() {
                return path.resolve('manage.py') + ' style --cssfile ' + path.resolve('scss/deps/py.lux');
            }
        }
    };
    //
    //  Additional JS tasks
    //  -----------------------
    //
    //  Tasks are loaded only if specified in the cfg
    //
    //  HTTP
    if (cfg.http) {
        grunt.loadNpmTasks('grunt-http');
        jsTasks.push('http');
    }
    //
    //  COPY
    if (cfg.copy) {
        grunt.loadNpmTasks('grunt-contrib-copy');
        jsTasks.push('copy');
    }
    //
    //  HTML2JS
    if (cfg.html2js) {
        jsTasks = ['html2js'].concat(jsTasks);
        grunt.loadNpmTasks('grunt-html2js');
    }
    //
    //  ESLINT
    if (cfg.eslint) {
        jsTasks = ['eslint'].concat(jsTasks);
        if (!cfg.eslint.options) cfg.eslint.options = {
            quiet: true
        };
        grunt.loadNpmTasks('grunt-eslint');
    }
    // CONCAT and UGLIFY always added at the end
    jsTasks = jsTasks.concat(['concat', 'uglify']);

    var buildTasks = baseTasks.concat(jsTasks),
        testTasks = baseTasks.concat(['karma:dev']);
    //
    //  Build CSS if required
    //  --------------------------
    //
    //  When the ``sass`` key is available in config, add the necessary tasks
    if (cfg.sass) {
        grunt.log.debug('Adding sass configuration');

        _.forOwn(cfg.sass, function(value, key) {
            if (skipEntries.indexOf(key) < 0) cssTasks.push('sass:' + key);
        });

        if (cssTasks.length) {
            grunt.loadNpmTasks('grunt-sass');
            cssTasks = ['shell:buildPythonCSS'].concat(cssTasks);

            if (!cfg.sass.options) cfg.sass.options = {
                sourceMap: true,
                sourceMapContents: true,
                includePaths: [path.join(__dirname, 'node_modules')]
            };

            // Add watch for sass files
            add_watch(cfg, 'sass', ['css']);

            if (cfg.cssmin) {
                grunt.loadNpmTasks('grunt-contrib-cssmin');

                _.forOwn(cfg.cssmin, function(value, key) {
                    if (skipEntries.indexOf(key) < 0) cssTasks.push('cssmin:' + key);
                });

                if (!cfg.cssmin.options) cfg.cssmin.options = {
                    shorthandCompacting: false,
                    roundingPrecision: -1,
                    sourceMap: true,
                    sourceMapInlineSources: true
                };
            }

            var buildCss = baseTasks.concat(cssTasks);
            buildTasks = buildTasks.concat(cssTasks);
            grunt.registerTask('css', 'Compile python and sass styles', buildCss);
        }
    }
    //
    //
    // Preprocess Javascript jslibs
    _.forOwn(jslibs, function(value, name) {
        var options = value.options;
        if (options && options.banner) {
            options.banner = grunt.file.read(options.banner);
        }
        add_watch(jslibs, name, jsTasks);
        if (value.dest) concats[name] = value;
    });
    //
    function uglify_jslibs() {
        var result = {};
        _.forOwn(concats, function(value, name) {
            if (name !== 'options' && value.minify !== false) {
                result[name] = {
                    dest: value.dest.replace('.js', '.min.js'),
                    src: [value.dest],
                    options: {
                        sourceMap: false, // TODO change to true when Chrome sourcemaps bug is fixed
                        sourceMapIn: value.dest + '.map',
                        sourceMapIncludeSources: false // TODO change to true when Chrome sourcemaps bug is fixed
                    }
                };
            }
        });
        return result;
    }

    // Initialise Grunt with all tasks defined above
    cfg.uglify = uglify_jslibs();
    // Main config is in karma.conf.js, with overrides below
    // We may want to set up an auto-watch config, see https://github.com/karma-runner/grunt-karma#running-tests
    cfg.karma = {
        options: {
            configFile: 'karma.conf.js'
        },
        ci: {
            browsers: ['PhantomJS'],
            coverageReporter: {
                includeAllSources: true,
                reporters: [{
                    subdir: '.',
                    type: 'cobertura',
                    dir: 'coverage/'
                }, {
                    subdir: '.',
                    type: 'lcovonly',
                    dir: 'coverage/'
                }, {
                    type: 'text-summary'
                }]
            }
        },
        phantomjs: {
            browsers: ['PhantomJS']
        },
        dev: {
            browsers: ['PhantomJS', 'Firefox', 'Chrome']
        },
        debug_chrome: {
            singleRun: false,
            browsers: ['Chrome'],
            preprocessors: {},
            coverageReporter: {},
            reporters: ['dots']
        },
        debug_firefox: {
            singleRun: false,
            browsers: ['Firefox'],
            preprocessors: {},
            coverageReporter: {},
            reporters: ['dots']
        }
    };

    //
    grunt.registerTask('luxbuild', 'Load lux configuration', function() {
        var paths = cfg.requirejs.compile.options.paths,
            filename = 'js/build/lux.json',
            obj = grunt.file.readJSON(filename);
        grunt.log.writeln('Read paths from "' + filename + '"');
        _.extend(paths, obj.paths);
    });

    //
    // These plugins provide necessary tasks.
    grunt.loadNpmTasks('grunt-contrib-requirejs', ['html2js']);
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-karma');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-shell');
    grunt.loadNpmTasks('grunt-contrib-clean');
    //

    grunt.registerTask('test', testTasks);
    grunt.registerTask('test:debug-chrome', ['karma:debug_chrome']);
    grunt.registerTask('test:debug-firefox', ['karma:debug_firefox']);
    grunt.registerTask('build', 'Compile and lint all libraries', buildTasks);
    grunt.registerTask('coverage', 'Test coverage using Jasmine and Istanbul', ['clean:test', 'karma:ci']);
    grunt.registerTask('all', 'Compile lint and test all libraries', ['build', 'test']);
    grunt.registerTask('default', ['build', 'karma:phantomjs']);
    //
    grunt.initConfig(cfg);

    //
    // Add a watch entry to ``cfg``
    function add_watch(obj, name, tasks) {
        var src = obj[name],
            watch = src ? src.watch : null;
        if (watch) {
            delete src.watch;
            if (!cfg.watch) cfg.watch = {
                options: {
                    atBegin: true,
                    // Start a live reload server on the default port 35729
                    livereload: true
                }
            };
            cfg.watch[name] = watch;
            if (!watch.tasks) {
                watch.tasks = tasks;
            }
        }
    }
};
