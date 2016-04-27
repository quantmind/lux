define(['angular',
        'lux/main',
        'lux/pagination/horizontal'], function(angular) {
    'use strict';

    /**
     * Pagination module
     *
     */
    angular.module('lux.pagination', ['lux.services', 'lux.pagination.horizontal'])
        //
        .factory('createPagination', ['paginationFactories', function (paginationFactories) {

            var createPagination = function (api, attrs) {
                var renderer = paginationFactories[attrs.type || 'horizontal'];

                if (renderer) return renderer(api, attrs);
            };

            return createPagination;
        }])
        /**
         * Directive to handle pagination.
         * Allows to use two types of pagination: horizontal (classic) and infinite (scroll)
         *
         * @params $compile
         * @params $templateCache
         * @params $injector
         */
        .directive('luxPagination', ['$lux', 'createPagination',
            function($lux, createPagination) {
                return {
                    restrict: 'AE',
                    link: function(scope, element, attrs) {
                        var target;
                        try {
                            target = angular.fromJson(attrs.target);
                        } catch (error) {
                            target = attrs.target;
                        }
                        var api = $lux.api(target);
                        if (api) {
                            scope.pag = createPagination(api, attrs);
                            scope.pag.getItems();
                        }
                    }
                };
            }
        ]);


});
