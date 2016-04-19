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

            var HorizontalPagination = function(pag, config) {
                this.pag = pag;
                this.items = [];
                this.total = 0;
                this.current = 1;
                this.last = 1;
                this.pages = [];
                this.maxRange = 8;
                angular.extend(this, horizontalDefaults, config);
            };

            paginationFactories['horizontal'] = HorizontalPagination;

            /**
             * Given the position in the sequence of pagination links [i], figure out what page number corresponds to that position
             *
             * @param i
             * @param currentPage
             * @param paginationRange
             * @param totalPages
             * @return {*}
             */
            HorizontalPagination.prototype.calculatePageNumber = function(i, currentPage, paginationRange, totalPages) {
                var halfWay = Math.ceil(paginationRange/2);

                if (i === paginationRange)
                    return totalPages;

                if (i === 1)
                    return i;

                if (paginationRange < totalPages) {
                    if (totalPages - halfWay < currentPage)
                        return totalPages - paginationRange + i;

                    if (halfWay < currentPage)
                        return currentPage - halfWay + i;
                }
                return i;
            };

            /**
             * Generate an array of page number (or the '...' string). It is used in an ng-repeat to generate the links for pages.
             *
             * @param currentPage
             * @param collectionLength
             * @param rowsPerPage
             * @param paginationRange
             * @returns {Array}
             */
            HorizontalPagination.prototype.generatePages = function(currentPage, collectionLength, rowsPerPage, paginationRange) {
                var pages = [];
                var totalPages = Math.ceil(collectionLength / rowsPerPage);
                var halfWay = Math.ceil(paginationRange / 2);
                var ellipsesNeeded = paginationRange < totalPages;
                var position;

                if (currentPage <= halfWay)
                    position = 'start';
                else if (totalPages - halfWay < currentPage)
                    position = 'end';
                else
                    position = 'middle';

                var i = 1;
                while (i <= totalPages && i <= paginationRange) {
                    var pageNumber = this.calculatePageNumber(i, currentPage, paginationRange, totalPages);
                    var openingEllipsesNeeded = (i === 2 && (position === 'middle' || position === 'end'));
                    var closingEllipsesNeeded = (i === paginationRange - 1 && (position === 'middle' || position === 'start'));

                    if (ellipsesNeeded && (openingEllipsesNeeded || closingEllipsesNeeded))
                        pages.push('...');
                    else
                        pages.push(pageNumber);

                    ++i;
                }
                return pages;
            };

            /**
             * Custom "track by" function which allows for duplicate "..." entries on long lists
             *
             * @param id
             * @param index
             * @returns {string}
             */
            HorizontalPagination.prototype.tracker = function(id, index) {
                return id + '_' + index;
            };

            /**
             * Called as the first function to fetch initial items from API
             */
            HorizontalPagination.prototype.init = function() {
                this.getItems();
            };

            /**
             * Called when page number was changed to get more data
             */
            HorizontalPagination.prototype.getItems = function() {
                var offset = parseInt(this.limit * (this.current - 1));
                this.items = [];

                this.luxApi.get({path: this.targetUrl}, {limit: parseInt(this.limit), offset: offset}).then(function(resp) {
                    this.total = resp.data.total;
                    this.last = this.getPageNumbers();

                    var items = resp.data.result;
                    for (var i = 0; i < items.length; i++)
                        this.items.push(items[i]);

                    this.pages = this.generatePages(this.current, this.total, this.limit, this.maxRange);

                }.bind(this));
            };

            /**
             * Calculates total number of pages
             *
             * @returns {number}
             */
            HorizontalPagination.prototype.getPageNumbers = function() {
                return Math.ceil(this.total/this.limit);
            };

            /**
             * Called when we change page number
             *
             * @param pageNumber
             */
            HorizontalPagination.prototype.gotoPage = function(pageNumber) {
                if (pageNumber === this.current) return;

                if (pageNumber >= 1 && pageNumber <= this.getPageNumbers()) {
                    this.current = pageNumber;
                    this.getItems();
                }
            };

            /**
             * Called when we go to the next page
             */
            HorizontalPagination.prototype.nextPage = function() {
                if (this.current < this.getPageNumbers()) {
                    ++this.current;
                    this.getItems();
                }
            };

            /**
             * Called when we go to the previous page
             */
            HorizontalPagination.prototype.prevPage = function() {
                if (this.current > 1) {
                    --this.current;
                    this.getItems();
                }
            };

            /**
             * Checks if the next page is disabled
             *
             * @returns {boolean}
             */
            HorizontalPagination.prototype.nextPageDisabled = function() {
                return this.current === this.getPageNumbers() ? 'disabled' : '';
            };

            /**
             * Checks if the previous page is disabled
             *
             * @returns {boolean}
             */
            HorizontalPagination.prototype.prevPageDisabled = function() {
                return this.current === 1 ? 'disabled' : '';
            };
        }])

        .factory('renderPagination', ['paginationFactories', function (paginationFactories) {

            var renderPagination = function (pag, element, attrs) {
                var Renderer = paginationFactories[attrs.type || 'horizontal'];

                if (Renderer) {
                    var renderer = new Renderer(pag, element, attrs);
                    renderer.init();
                }
            };

            return renderPagination;
        }]);
});
