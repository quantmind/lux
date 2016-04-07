define(['angular',
        'lux/main'], function(angular) {
    'use strict';

    /**
     * Infinite pagination module
     *
     *   Usage:
     *      <pagination data-type="infinite"
     *                  data-scroll-distance="1"
     *                  data-load-more-button="true"
                        data-display-loading-name="datasets"
     *                  data-url="/users"
     *                  data-limit="6">
     *          <ul>
     *              <li ng-repeat="item in pagination.items">
     *                 <span>{{item}}</span>
     *              </li>
     *          </ul>
     *      </pagination>
     */
    angular.module('lux.pagination.infinite', ['infinite-scroll'])
        /**
         * Default options
         */
        .constant('infiniteDefaults', {
            'loadMoreButton': {
                enabled: true,
                clicked: false
            },
            'limit': 5,
            'scrollDistance': 0,
            'templateUrl': 'lux/pagination/templates/infinite.tpl.html'
        })
        //
        .value('THROTTLE_MILLISECONDS', 400)
        /**
         * Factory to handle infinite pagination
         *
         * @param $lux
         * @param infiniteDefaults
         */
        .factory('InfinitePagination', ['$lux', 'infiniteDefaults', function($lux, infiniteDefaults) {
            var InfinitePagination = function(config) {
                this.items = [];
                this.busy = false;
                this.offset = 0;
                this.total = null;
                this.luxApi = $lux.api(config.API_URL);
                angular.extend(this, infiniteDefaults, config);
                if (!this.scrollDistance) {
                    this.scrollDistance = infiniteDefaults.scrollDistance;
                }
            };

            /**
             * Called as the first function to fetch initial items from API
             */
            InfinitePagination.prototype.init = function() {
                this.nextPage();
            };

            /**
             * Called when click load more button
             */
            InfinitePagination.prototype.loadMore = function() {
                this.loadMoreButton.clicked = true;
                this.nextPage();
                this.loadMoreButton.clicked = false;
            };

            /**
             * Checking whether data was downloaded
             *
             * @returns {boolean}
             */
            InfinitePagination.prototype.isLoadDone = function() {
                return (this.total && this.items.length === this.total);
            };

            InfinitePagination.prototype.isLoadMoreHidden = function() {
                return !this.loadMoreButton.enabled || this.loadMoreButton.clicked || this.isLoadDone();
            };

            /**
             * Prevents to do more API calls at the same time
             *
             * @returns {boolean}
             */
            InfinitePagination.prototype.paused = function() {
                return this.busy || this.isLoadDone();
            };

            /**
             * Called when more data is being loaded
             */
            InfinitePagination.prototype.nextPage = function() {
                if (this.paused())
                    return;

                if (this.loadMoreButton.enabled) {
                    var isFirstLoad = (this.total === null);

                    if (!isFirstLoad && !this.loadMoreButton.clicked)
                        return;
                }

                this.busy = true;

                this.luxApi.get({path: this.targetUrl}, {limit: parseInt(this.limit), offset: parseInt(this.items.length)}).then(function(resp) {
                    this.total = resp.data.total;

                    var items = resp.data.result;
                    for (var i = 0; i < items.length; i++)
                        this.items.push(items[i]);

                    this.busy = false;
                }.bind(this));
            };

            return InfinitePagination;
        }]);
});
