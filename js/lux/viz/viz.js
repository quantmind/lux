    //
    // Load d3 extensions into angular
    lux.addD3ext = function (d3ext) {

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
                            self.attrs.data = response.data;
                            callback();
                            return response;
                        });
                    }
                } else if (src) {
                    this.d3.json(src, function(error, json) {
                        if (!error) {
                            self.attrs.data = json || {};
                            return callback();
                        }
                    });
                }
            };
        }

        var app = angular.module('d3viz', ['lux.services']);

        angular.forEach(d3ext, function (VizClass, name) {

            if (VizClass instanceof d3ext.Viz) {
                var dname = 'viz' + name.substring(0,1).toUpperCase() + name.substring(1);

                app.directive(dname, ['$lux', function ($lux) {
                    return {
                            //
                            // Create via element tag or attribute
                            restrict: 'AE',
                            //
                            link: function (scope, element, attrs) {
                                attrs = lux.getDirectiveOptions(attrs);
                                var viz = new VizClass(element, attrs);
                                viz.loadData = loadData($lux);
                                viz.build();
                            }
                        };
                }]);
            }
        });
    };
