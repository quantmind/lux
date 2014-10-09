/*jshint node: true */
/*global config:true, task:true, process:true*/
module.exports = function (grunt) {
  "use strict";
    // Project configuration.
    var docco_output = '../docs/lux/html/docco',
        // All libraries
        libs = grunt.file.readJSON('js/libs.json'),
        allHtml2js = {},
        buildTasks = ['gruntfile', 'concat', 'jshint', 'uglify'],
        cfg = {
            pkg: grunt.file.readJSON('package.json'),
            concat: libs,
            jasmine: {
                src : 'lux/media/lux/lux.min.js',
                options : {
                    specs : 'js/tests/*.js',
                    template: require('grunt-template-jasmine-requirejs'),
                    templateOptions: {
                        requireConfig: {
                            paths: {
                                angular: "node_modules/angular/lib/angular.min"
                            },
                            shim: {
                                angular: {
                                    exports: "angular"
                                }
                            }
                        }
                    }
                }
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
    function docco_libs () {
        var src = [];
        for_each(libs, function (name) {
            src.push(this.dest);
        });
        return {
            docs: {
                'src': src,
                options: {
                    output: docco_output
                }
            }
        };
    }
    //
    // js hint all libraries
    function jshint_libs () {
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
    cfg.uglify = uglify_libs();
    cfg.jshint = jshint_libs();
    //cfg.docco = docco_libs();
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
    //grunt.loadNpmTasks('grunt-contrib-watch');
    //grunt.loadNpmTasks('grunt-docco');
    //
    grunt.registerTask('gruntfile', 'jshint Gruntfile.js',
            ['jshint:gruntfile']);
    grunt.registerTask('build', 'Compile and lint all Lux libraries', buildTasks);
    grunt.registerTask('all', 'Build and test', ['build', 'jasmine']);
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
