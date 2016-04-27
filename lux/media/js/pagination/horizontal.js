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

            paginationFactories['horizontal'] = function (api, config) {
                config = angular.extend({}, horizontalDefaults, config);
                return horizontalPagination(api, config);
            };

        }]);


    function horizontalPagination (api, config) {
        var pag = {};

        pag.limit = parseInt(config.limit) || 25;
        pag.current = 1;

        /**
         * Called when page number was changed to get more data
         */
        pag.getItems = function () {
            var offset = pag.limit * (pag.current - 1);

            api.get(null, {
                limit: pag.limit,
                offset: offset
            }).then(function (resp) {
                var data = resp.data;
                pag.total = data.total;
                pag.first = data.first;
                pag.next = data.next;
                pag.last = data.last;
                // last = getPageNumbers();

                pag.items = resp.data.result;
                pag.pages = generatePages();
            });
        };

        return pag;

        function generatePages () {

        }
    }
});
