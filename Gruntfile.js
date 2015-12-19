/*jshint node: true */
/*global config:true, task:true, process:true*/
module.exports = function (grunt) {
    "use strict";
    // bmll configuration.
    var lux_root = '',
        //
        lux_dir = lux_root + 'lux/media/lux',
        lux_libs = grunt.file.readJSON(lux_dir + 'libs.json'),
        libs = grunt.file.readJSON('js/libs.json'),
        path = require('path'),
        buildTasks = ['gruntfile', 'html2js', 'requirejs', 'http', 'copy', 'concat', 'jshint', 'uglify', 'css'],
        concats = {
            options: {
                sourceMap: false // TODO change to true when Chrome sourcemaps bug is fixed
            }
        },
        cfg = {
            pkg: grunt.file.readJSON('package.json'),
            requirejs: {
                compile: {
                    options: {
                        baseUrl: 'js/',
                        generateSourceMaps: false, // TODO change to true when Chrome sourcemaps bug is fixed
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
                        out: 'js/build/bundle.js',
                        optimize: 'none'
                    }
                }
            },
            concat: concats,
            http: {
                cfg: {
                    options: {
                        url: 'https://raw.githubusercontent.com/quantmind/lux/' + lux_branch + '/lux/media/lux/cfg.js'
                    },
                    dest: 'js/deps/cfg.js'
                },
                lux: {
                    options: {
                        url: 'https://raw.githubusercontent.com/quantmind/lux/' + lux_branch + '/lux/media/lux/lux.js'
                    },
                    dest: 'js/deps/lux.js'
                },
                giotto: {
                    options: {
                        url: 'https://raw.githubusercontent.com/quantmind/giotto/master/dist/giotto.js'
                    },
                    dest: 'bmllportal/media/bmll/giotto.js'
                },
                giotto_min: {
                    options: {
                        url: 'https://raw.githubusercontent.com/quantmind/giotto/master/dist/giotto.min.js'
                    },
                    dest: 'bmllportal/media/bmll/giotto.min.js'
                }
            },
            copy: {
                ngImgCrop: {
                    expand: true,
                    src: ['node_modules/ng-img-crop/compile/minified/ng-img-crop.js'],
                    dest: 'bmllportal/media/bmll/',
                    flatten: true,
                    filter: 'isFile'
                }
            },
            clean: {
                build: {
                    src: ['scss/deps/*.css']
                }
            },
            shell: {
                buildPythonCSS: {
                    options: {
                        stdout: true,
                        stderr: true
                    },
                    command: function() {
                        return path.resolve('manage.py') + ' style --cssfile ' + path.resolve('scss/deps/bmll-lux');
                    }
                }
            },
            sass: {
                options: {
                    sourceMap: true,
                    sourceMapContents: true,
                    includePaths: [path.join(__dirname, 'node_modules')]
                },
                bmll: {
                    files: {
                        'bmllportal/media/bmll/bmll.css': 'scss/bmll.scss'
                    }
                }
            },
            cssmin: {
                options: {
                    shorthandCompacting: false,
                    roundingPrecision: -1,
                    sourceMap: true,
                    sourceMapInlineSources: true
                },
                bmll: {
                    files: {
                      'bmllportal/media/bmll/bmll.min.css': ['bmllportal/media/bmll/bmll.css']
                    }
                }
            },
            watch: {
                options: {
                    atBegin: true,
                    // Start a live reload server on the default port 35729
                    livereload: true
                },
                main: {
                    files: ['js/**/*.js',
                        '!js/build/**/*.js',
                        '!js/tests/**/*.js',
                        'js/**/*.tpl.html'],
                    tasks: ['html2js', 'requirejs', 'copy', 'concat', 'uglify', 'jshint']
                },
                css: {
                    files: ['scss/**/*.scss',
                        'scss/**/*.sass',
                        'bmllportal/css/*.py'],
                    tasks: ['css'],
                }
            }
        };
    //
    function for_each(obj, callback) {
        for (var p in obj) {
            if (obj.hasOwnProperty(p)) {
                callback.call(obj[p], p);
            }
        }
    }

    //
    // html2js is special, add html2js task if available
    if (libs.html2js) {
        cfg.html2js = libs.html2js;
        delete libs.html2js;
        grunt.log.debug('Adding html2js task');
        grunt.loadNpmTasks('grunt-html2js');
        buildTasks.splice(0, 0, 'html2js');
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
                    jQuery: true,
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
    // This Grunt Config Entry
    // -------------------------------
    // This Grunt Config Entry
    // -------------------------------
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
    // These plugins provide necessary tasks.
    grunt.loadNpmTasks('grunt-contrib-requirejs', ['html2js']);
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

    grunt.registerTask('test', ['html2js', 'karma:dev']);
    grunt.registerTask('test:debug-chrome', ['karma:debug_chrome']);
    grunt.registerTask('test:debug-firefox', ['karma:debug_firefox']);
    grunt.registerTask('gruntfile', 'jshint Gruntfile.js',
        ['jshint:gruntfile']);
    grunt.registerTask('build', 'Compile and lint all libraries', buildTasks);
    grunt.registerTask('coverage', 'Test coverage using Jasmine and Istanbul',
        ['karma:ci']);
    grunt.registerTask('all', 'Compile lint and test all libraries',
        ['build', 'test']);
    grunt.registerTask('css', 'Compile python and sass styles',
        ['clean:build', 'shell:buildPythonCSS', 'sass:bmll', 'cssmin:bmll']);
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
