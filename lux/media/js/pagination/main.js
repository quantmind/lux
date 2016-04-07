define(['angular',
        'lux/services/pagination',
        'lux/pagination/templates',
        'lux/pagination/horizontal',
        'lux/pagination/infinite',
        'angular-infinite-scroll'], function(angular) {
    'use strict';

    /**
     * Pagination module
     *
     */
    angular.module('lux.pagination', ['lux.pagination.templates', 'lux.pagination.horizontal', 'lux.pagination.infinite'])
        /**
         * Directive to handle pagination. It gets data from API via $lux service.
         * Allows to use two types of pagination: horizontal (classic) and infinite (scroll)
         *
         * @params $compile
         * @params $templateCache
         * @params $injector
         */
        .directive('luxPagination', ['$compile', '$templateCache', '$injector', function($compile, $templateCache, $injector) {
            return {
                restrict: 'E',
                transclude: true,
                scope: false,
                link: function(scope, element, attrs, ctrl, transcludeFn) {
                    var template,
                        PaginationService,
                        config = {
                            targetUrl: attrs.url,
                            limit: attrs.limit,
                            loadMoreButton: {
                                enabled: (attrs.loadMoreButton === 'true') || false
                            },
                            // displayLoadingName is displayed as `Loading <displayLoadingName> ...`
                            displayLoadingName: (attrs.displayLoadingName) || 'data',
                            scrollDistance: (attrs.scrollDistance) || false,
                            API_URL: scope.API_URL
                        };

                    if (attrs.limit)
                        config.limit = attrs.limit;

                    if (attrs.type === 'infinite')
                        PaginationService = $injector.get('InfinitePagination');
                    else
                        PaginationService = $injector.get('HorizontalPagination');

                    scope.pagination = new PaginationService(config);
                    scope.pagination.init();
                    template = $templateCache.get(scope.pagination.templateUrl);

                    // First we append transcluded content
                    var transContent = transcludeFn();
                    element.append(transContent);

                    // Then we can add pagination template
                    element.append($compile(template)(scope));
                }
            };
        }]);
});
