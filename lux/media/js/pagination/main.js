define(['angular',
        'lux/services/pagination',
        'lux/pagination/horizontal'], function(angular) {
    'use strict';

    /**
     * Pagination module
     *
     */
    angular.module('lux.pagination', ['lux.services.pagination', 'lux.pagination.horizontal'])
        /**
         * Directive to handle pagination.
         * Allows to use two types of pagination: horizontal (classic) and infinite (scroll)
         *
         * @params $compile
         * @params $templateCache
         * @params $injector
         */
        .directive('luxPagination', ['luxPaginationFactory', 'renderPagination',
            function(luxPagination, renderPagination) {
                return {
                    restrict: 'AE',
                    link: function(scope, element, attrs) {
                        var pag = luxPagination(scope, attrs.target);
                        renderPagination(pag, element, attrs);
                    }
                };
            }
        ]);
});
