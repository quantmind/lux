/*jshint node: true */
/*global config:true, task:true, process:true*/
module.exports = function (grunt) {
    "use strict";
    var base_dir = 'lux/media/js/',
        test_src = ['lux/media/lux/lux.js'],
        test_dependencies = [
        'angular-ui-select',
        'angular-ui-grid',
        'angular-mocks',
        'angular-strap',
        'angular-file-upload',
        'codemirror',
        'angular-touch',
        'lodash'
    ];
    // Project configuration.
    var libs = grunt.file.readJSON(base_dir + 'libs.json'),
        buildTasks = ['gruntfile', 'concat', 'jshint', 'uglify'],
        cfg = {
            pkg: grunt.file.readJSON('package.json'),
            concat: libs,
            jasmine: {
                test: {
                    src : test_src,
                    options : {
                        specs : base_dir + 'tests/**/*.js',
                        template: base_dir + 'tests/test.tpl.html',
                        templateOptions: {
                            deps: test_dependencies
                        }
                    }
                },
                coverage: {
                    src: test_src,
                    options: {
                        specs: base_dir + 'tests/**/*.js',
                        template: require('grunt-template-jasmine-istanbul'),
                        templateOptions: {
                            coverage: 'coverage/coverage.json',
                            report: [
                                {
                                    type: 'lcov',
                                    options: {
                                        dir: 'coverage'
                                    }
                                },
                                {
                                    type: 'html',
                                    options: {
                                        dir: 'coverage'
                                    }
                                },
                                {
                                    type: 'text-summary'
                                }
                            ],
                            template: base_dir + 'tests/test.tpl.html',
                            templateOptions: {
                                deps: test_dependencies
                            }
                        }
                    }
                }
            },
            watch: {
                options: {
                    atBegin: true,
                    livereload: true
                },
                files: [
                    '<%= concat.lux.src %>',
                    base_dir + '**/*.tpl.html'
                ],
                tasks: ['html2js', 'concat', 'jshint', 'uglify', 'jasmine:test']
            }
        };
    //
    // for_each function
    function for_each(obj, callback) {
        for(var p in obj) {
            if(obj.hasOwnProperty(p)) {
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

    // Add copy tasks if available
    if (libs.copy) {
        cfg.copy = libs.copy;
        buildTasks.push('copy');
        grunt.loadNpmTasks('grunt-contrib-copy');
        delete libs.copy;
    }
    //
    // Preprocess libs
    for_each(libs, function (name) {
        var options = this.options;
        if(options && options.banner) {
            options.banner = grunt.file.read(options.banner);
        }
    });
    //
    function uglify_libs () {
        var result = {};
        for_each(libs, function (name) {
            if (this.minify !== false)
                result[name] = {dest: this.dest.replace('.js', '.min.js'),
                                src: [this.dest]};
        });
        return result;
    }
    //
    // js hint all libraries
    function jshint_libs () {
        var result = {
            gruntfile: "Gruntfile.js",
            options: {
                browser: true,
                expr: true,
                evil: true,
                globals: {
                    lux: true,
                    requirejs: true,
                    require: true,
                    exports: true,
                    console: true,
                    DOMParser: true,
                    Showdown: true,
                    prettyPrint: true,
                    module: true,
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
    cfg.uglify = uglify_libs();
    cfg.jshint = jshint_libs();
    //
    // Initialise Grunt with all tasks defined above
    grunt.initConfig(cfg);
    //
    // These plugins provide necessary tasks.
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-jasmine');
    //grunt.loadNpmTasks('grunt-contrib-nodeunit');
    grunt.loadNpmTasks('grunt-contrib-watch');
    //grunt.loadNpmTasks('grunt-docco');
    //
    grunt.registerTask('gruntfile', 'jshint Gruntfile.js',
            ['jshint:gruntfile']);
    grunt.registerTask('build', 'Compile and lint all Lux libraries', buildTasks);
    grunt.registerTask('coverage', 'Test coverage using Jasmine and Istanbul', ['jasmine:coverage']);
    grunt.registerTask('all', 'Build and test', ['build', 'jasmine:test']);
    grunt.registerTask('default', ['all']);
    //
    for_each(libs, function (name) {
        var tasks = ['concat:' + name, 'jshint:' + name];
        if (this.minify !== false)
            tasks.push('uglify:' + name);
        //
        grunt.registerTask(name,
            'Compile & lint "' + name + '" library into ' + this.dest, tasks);
    });
};
