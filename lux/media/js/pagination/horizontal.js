define(['angular',
        'lux/main',
        'lux/pagination/templates'], function(angular) {
    'use strict';

    /**
     * Horizontal pagination module
     *
     *   Usage:
     *      <pagination data-url="/users" data-limit="6">
     *          <ul>
     *              <li ng-repeat="item in pagination.items">
     *                 <span>{{item}}</span>
     *              </li>
     *          </ul>
     *      </pagination>
     */
    angular.module('lux.pagination.horizontal', ['lux.pagination.templates'])
        /**
         * Default opitons
         */
        .constant('paginationFactories', {})
        //
        .constant('horizontalDefaults', {
            'limit': 5,
            'templateUrl': 'lux/pagination/templates/horizontal.tpl.html'
        })
        /**
         * Factory to handle horizontal pagination
         *
         * @param $lux
         * @param horizontalDefaults
         */
        .config(['paginationFactories', 'horizontalDefaults', function(paginationFactories, horizontalDefaults) {

            paginationFactories['horizontal'] = function (api, scope, element, config) {
                config = angular.extend({}, horizontalDefaults, config);
                return horizontalPagination(api, scope, element, config);
            };

        }])

        .factory('createPagination', ['paginationFactories', function (paginationFactories) {

            var createPagination = function (api, scope, element, attrs) {
                var renderer = paginationFactories[attrs.type || 'horizontal'];

                if (renderer) {
                    scope.pag = renderer(api, scope, element, attrs);
                    scope.pag.getItems();
                }
            };

            return createPagination;
        }]);


    function horizontalPagination (api, scope, element, config) {
        var pag = {},
            limit = parseInt(config.limit) || 25,
            current = 1;

        /**
         * Called when page number was changed to get more data
         */
        pag.getItems = function () {
            var offset = limit * (current - 1);

            api.get(null, {
                limit: limit,
                offset: offset
            }, function (resp) {
                scope.total = resp.data.total;
                // last = getPageNumbers();

                scope.items = resp.data.result;
                scope.pages = generatePages();
            });
        };

        return pag;

        function generatePages () {

        }
    }
});
