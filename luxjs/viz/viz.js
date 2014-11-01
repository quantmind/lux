
    lux.d3Directive = function (name, VizClass, moduleName) {

        moduleName = moduleName || 'd3viz';

        var dname = 'viz' + name.substring(0,1).toUpperCase() + name.substring(1);

        function loadData ($lux) {

            return function (callback) {
                var self = this,
                    src = this.attrs.src;
                if (typeof src === 'object') {
                    var id = src.id,
                        api = $lux.api(src);
                    if (api) {
                        var p = id ? api.get(id) : api.getList();
                        p.then(function (response) {
                            self.setData(response.data, callback);
                            return response;
                        });
                    }
                } else if (src) {
                    d3.json(src, function(error, json) {
                        if (!error) {
                            self.setData(json, callback);
                            return self.attrs.data;
                        }
                    });
                }
            };
        }

        // Obtain extra information from javascript objects
        function getOptions(d3, attrs) {
            if (typeof attrs.options === 'string') {
                var obj = root,
                    bits= attrs.options.split('.');

                for (var i=0; i<bits.length; ++i) {
                    obj = obj[bits[i]];
                    if (!obj) break;
                }
                if (typeof obj === 'function')
                    obj = obj(d3, attrs);
                attrs = extend(attrs, obj);
            }
            return attrs;
        }

        angular.module(moduleName)
            .directive(dname, ['$lux', function ($lux) {
                return {
                        //
                        // Create via element tag or attribute
                        restrict: 'AE',
                        //
                        link: function (scope, element, attrs) {
                            var viz = element.data(dname);
                            if (!viz) {
                                var options = getOptions(d3, attrs),
                                    autoBuild = options.autoBuild;
                                options.autoBuild = false;
                                // add scope to the options
                                options.scope = scope;
                                viz = new VizClass(element[0], options);
                                element.data(viz);
                                viz.loadData = loadData($lux);
                                if (autoBuild === undefined || autoBuild)
                                    viz.build();
                            }
                        }
                    };
            }]);
    };
    //
    // Load d3 extensions into angular 'd3viz' module
    //  d3ext is the d3 extension object
    //  name is the optional module name for angular (default to d3viz)
    lux.addD3ext = function (d3) {
        //
        var moduleName = 'd3viz';

        // Loop through d3 extensions and create directives
        // for each Visualization class
        angular.forEach(d3.ext, function (VizClass, name) {
            if (d3.ext.isviz(VizClass)) {
                lux.d3Directive(name, VizClass, moduleName);
            }
        });

        return lux;
    };

    angular.module('d3viz', ['lux.services'])
        .directive('jstats', function () {
            return {
                link: function (scope, element, attrs) {
                    var mode = attrs.mode ? +attrs.mode : 1;
                    require(rcfg.min(['stats']), function () {
                        var stats = new Stats();
                        stats.setMode(mode);
                        scope.stats = stats;
                        element.append($(stats.domElement));
                    });
                }
            };
        });
