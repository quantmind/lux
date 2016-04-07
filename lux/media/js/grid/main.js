define(['angular',
        'lux/main',
        'lux/grid/providers',
        'lux/grid/api',
        'lux/grid/menu'], function (angular, lux) {
    'use strict';

    angular.module('lux.grid', ['lux.grid.api', 'lux.grid.menu'])
        //
        // Directive to build Angular-UI grid options using Lux REST API
        .directive('luxGrid', ['luxGridApi', function (luxGridApi) {

            return {
                restrict: 'A',
                link: {
                    pre: function (scope, element, attrs) {
                        var scripts = element[0].getElementsByTagName('script'),
                            opts = lux.getOptions(attrs, 'luxGrid');

                        angular.forEach(scripts, function (js) {
                            lux.globalEval(js.innerHTML);
                        });

                        luxGridApi(scope, element, opts);
                    }
                }
            };
        }]);
});
