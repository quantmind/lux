
    angular.module('lux.grid', ['ngTouch', 'ui.grid'])

        // Directive to build Angular-UI grid options using Lux REST API
        .directive('restGrid', ['$lux', function ($lux) {

            // Pre-process grid options
            function buildOptions (options) {

                var api = $lux.api(options.target),
                    columns = options.columns;

                return {
                    columnDefs: []
                };
            }


            return {
                restrict: 'A',
                link: {
                    pre: function (scope, element, attrs) {
                        var scripts= element[0].getElementsByTagName('script');

                        forEach(scripts, function (js) {
                            globalEval(js.innerHTML);
                        });

                        var opts = attrs;
                        if (attrs.restGrid) opts = {options: attrs.restGrid};

                        opts = getOptions(opts);

                        if (opts)
                            scope.gridOptions = buildOptions(opts);
                    }
                }
            };

        }]);
