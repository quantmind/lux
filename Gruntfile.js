/*jshint node: true */
/*global config:true, task:true, process:true*/
module.exports = function (grunt) {
    "use strict";
    // configuration.
    var src_root = 'luxsite/media/',
        //
        config_file = src_root + 'config.json',
        cfg = grunt.file.readJSON(config_file),
        libs = cfg.js,
        path = require('path'),
        _ = require('lodash'),
        baseTasks = ['gruntfile', 'shell:buildLuxConfig', 'luxbuild'],
        jsTasks = ['requirejs'],
        cssTasks = [],
        skipEntries = ['options', 'watch'],
        concats = {
            options: {
                sourceMap: false // TODO change to true when Chrome sourcemaps bug is fixed
            }
        };

    if (!libs) {
        grunt.log.error('"js" entry not available in "' + config_file + '"');
        return grunt.failed;
    }

    delete cfg.js;

    cfg.pkg = grunt.file.readJSON('package.json');
    cfg.requirejs = {
        compile: {
            options: {
                baseUrl: src_root + 'js',
                generateSourceMaps: false, // TODO change to true when Chrome sourcemaps bug is fixed
                paths: {
                    angular: 'empty:',
                    d3: 'empty:',
                    'giotto': 'empty:',
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
                    'angular-scroll': 'empty:', // TODO find out who is using this
                    'angular-ui-select': 'empty:', // TODO find out who is using this
                    'angular-ui-router': 'empty:',
                    'angular-strap-tpl': 'empty:',
                    'moment-timezone': 'empty:',
                    'lodash': 'empty:'
                },
                name: 'app',
                out: src_root + 'build/bundle.js',
                optimize: 'none'
            }
        }
    };
    cfg.concat = concats;

    // Build lux configuration file read by ``luxbuild`` task
    cfg.shell = {
        buildLuxConfig: {
            options: {
                stdout: true,
                stderr: true
            },
            command: function() {
                return path.resolve('manage.py') + ' grunt';
            }
        }
    };

    if (cfg.http) jsTasks.push('http');
    if (cfg.copy) jsTasks.push('copy');
    jsTasks = jsTasks.concat(['concat', 'jshint', 'uglify']);

    var buildTasks = baseTasks.concat(jsTasks),
        testTasks = baseTasks.concat(['karma:dev']);

    //
    // Build CSS if required
    if (cfg.sass) {
        grunt.log.debug('Adding sass configuration');

        _.forOwn(cfg.sass, function (value, key) {
            if (skipEntries.indexOf(key) < 0) cssTasks.push('sass:' + key);
        });

        if (cssTasks.length) {
            buildTasks.push('css_only');

            if (!cfg.sass.options)
                cfg.sass.options = {
                    sourceMap: true,
                    sourceMapContents: true,
                    includePaths: [path.join(__dirname, 'node_modules')]
                };

            if (cfg.cssmin) {
                _.forOwn(cfg.cssmin, function (value, key) {
                    if (skipEntries.indexOf(key) < 0) cssTasks.push('cssmin:' + key);
                });

                if (!cfg.cssmin.options)
                    cfg.cssmin.options = {
                        shorthandCompacting: false,
                        roundingPrecision: -1,
                        sourceMap: true,
                        sourceMapInlineSources: true
                    };
            }
        }
    }

    // Watch
    if (cfg.watch) {
        var watch = {};
        _.forOwn(cfg.sass, function (value, key) {
            if (skipEntries.indexOf(key) < 0) {
                if (_.isArray(value)) value = {files: value};
                if (!value.tasks) value.tasks = jsTasks;
                watch[key] = value;
            }
        });

        watch.options = cfg.watch.options;
        if (!watch.options)
            watch.options = {
                atBegin: true,
                // Start a live reload server on the default port 35729
                livereload: true
            };

        cfg.watch = watch;
    }
    //
    function for_each(obj, callback) {
        for (var p in obj) {
            if (obj.hasOwnProperty(p)) {
                callback.call(obj[p], p);
            }
        }
    }
    //
    // Preprocess libs
    for_each(libs, function (name) {
        var options = this.options;
        if (options && options.banner) {
            options.banner = grunt.file.read(options.banner);
        }
        if (this.dest)
            concats[name] = this;
    });
    //
    function uglify_libs() {
        var result = {};
        for_each(concats, function (name) {
            if (name !== 'options' && this.minify !== false) {
                result[name] = {
                    dest: this.dest.replace('.js', '.min.js'),
                    src: [this.dest],
                    options: {
                        sourceMap: false, // TODO change to true when Chrome sourcemaps bug is fixed
                        sourceMapIn: this.dest + '.map',
                        sourceMapIncludeSources: false // TODO change to true when Chrome sourcemaps bug is fixed
                    }
                };
            }
        });
        return result;
    }

    //
    // js hint all libraries
    function jshint_libs() {
        var result = {
            gruntfile: "Gruntfile.js",
            options: {
                browser: true,
                expr: true,
                globals: {
                    $: true,
                    lux: true,
                    requirejs: true,
                    require: true,
                    exports: true,
                    console: true,
                    DOMParser: true,
                    Showdown: true,
                    prettyPrint: true,
                    module: true,
                    ok: true,
                    equal: true,
                    test: true,
                    asyncTest: true,
                    start: true
                }
            }
        };
        for_each(libs, function (name) {
            result[name] = this.dest;
        });
        return result;
    }

    //
    // Initialise Grunt with all tasks defined above
    cfg.uglify = uglify_libs();
    cfg.jshint = jshint_libs();
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
                },{
                    subdir: '.',
                    type: 'lcovonly',
                    dir: 'coverage/'
                },{
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
    grunt.initConfig(cfg);
    //
    grunt.registerTask('luxbuild', 'Load lux configuration', function () {
        var paths = cfg.requirejs.compile.options.paths,
            filename = src_root + 'build/lux.json',
            obj = grunt.file.readJSON(filename);
        grunt.log.writeln('Read paths from "' + filename + '"');
        _.extend(paths, obj.paths);
        //_.forOwn(paths, function (value, key) {
        //    grunt.log.writeln(key + ': ' + value);
        //});
    });
    //
    // These plugins provide necessary tasks
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-karma');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-http');
    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-shell');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-clean');
    //

    grunt.registerTask('test', testTasks);
    grunt.registerTask('test:debug-chrome', ['karma:debug_chrome']);
    grunt.registerTask('test:debug-firefox', ['karma:debug_firefox']);
    grunt.registerTask('gruntfile', 'jshint Gruntfile.js',
        ['jshint:gruntfile']);
    grunt.registerTask('build', 'Compile and lint all libraries', buildTasks);
    grunt.registerTask('coverage', 'Test coverage using Jasmine and Istanbul',
        ['karma:ci']);
    grunt.registerTask('all', 'Compile lint and test all libraries',
        ['build', 'test']);

    if (cssTasks.length) {
        var allCssTasks = ['css_only'];
        grunt.registerTask('css_only', 'Compile sass styles', cssTasks);
        grunt.registerTask('css', 'Compile sass styles', allCssTasks);
    }
    grunt.registerTask('default', ['build', 'karma:phantomjs']);
    //
    for_each(libs, function (name) {
        var tasks = [];
        if (concats[name]) tasks.push('concat:' + name);
        tasks.push('jshint:' + name);
        if (this.minify !== false) tasks.push('uglify:' + name);
        //
        grunt.registerTask(name, tasks.join(', '), tasks);
    });
};
