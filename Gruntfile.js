/*jshint node: true */
/*global config:true, task:true, process:true*/
module.exports = function(grunt) {
  "use strict";
    // Project configuration.
    var docco_output = '../docs/lux/html/docco',
        //docco_output = 'docs/build/html/docco',
        // All libraries
        libs = {
            lux: grunt.file.readJSON('js/lux/lib.json'),
            lorem: grunt.file.readJSON('js/lorem/lib.json')
        };
    //
    function for_each(obj, callback) {
        for(var p in obj) {
            if(obj.hasOwnProperty(p)) {
                callback.call(obj[p], p);
            }
        }
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
            result[name] = {dest: this.dest.replace('.js', '.min.js'),
                            src: ['<banner>', this.dest]};
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
    //
    // Initialise Grunt with all tasks defined above
    grunt.initConfig({
        pkg: grunt.file.readJSON('lux/package.json'),
        concat: libs,
        uglify: uglify_libs(),
        jshint: jshint_libs(),
        docco: docco_libs(),
        qunit: {
            files: "test/index.html"
        }
    });
    //
    // These plugins provide necessary tasks.
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-concat');
    //grunt.loadNpmTasks('grunt-contrib-nodeunit');
    //grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-docco');
    //
    grunt.registerTask('gruntfile', 'jshint Gruntfile.js',
            ['jshint:gruntfile']);
    grunt.registerTask('all', 'Compile and lint all Lux libraries',
            ['concat', 'jshint', 'uglify', 'docco']);
    grunt.registerTask('default', ['all']);
    //
    for_each(libs, function (name) {
        grunt.registerTask(name,
                'Compile & lint "' + name + '" library into ' + this.dest,
                ['concat:' + name, 'jshint:' + name, 'uglify:' + name]);
    });
};
