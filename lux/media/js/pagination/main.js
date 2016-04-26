define(['angular',
        'lux/main',
        'lux/pagination/horizontal'], function(angular, lux) {
    'use strict';

    /**
     * Pagination module
     *
     */
    angular.module('lux.pagination', ['lux.services', 'lux.pagination.horizontal'])
        //
        .factory('luxPagination', ['$lux', function ($lux) {


            function luxPaginationFactory (scope, target, recursive) {
                var api = $lux.api(target);
                return new LuxPagination(api, scope, recursive);
            }

            return luxPaginationFactory;

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
                        if (api) createPagination(api, scope, element, attrs);
                    }
                };
            }
        ]);


    /**
    * LuxPagination constructor requires three args
    * @param scope - the angular $scope of component's directive
    * @param target {object} - containing name and url, e.g.
    * {name: "groups_url", url: "http://127.0.0.1:6050"}
    * @param recursive {boolean}- set to true if you want to recursively
    * request all data from the endpoint
    */
    function LuxPagination(api, scope, recursive) {
        this.api = api;
        this.scope = scope;
        this.recursive = recursive === true ? true : false;
        this.searchField = null;
    }


    LuxPagination.prototype.getData = function(params, callBack, errorBack) {
        // getData runs $lux.api.get() followed by the component's
        // callback on the returned data or error.
        // it's up to the component to handle the error.
        callBack = callBack || lux.noop;
        errorBack = errorBack || callBack;

        this.api.get(null, params).then(function(data) {
            callBack(data);
            this.updateUrls(data);

        }, function(error) {

            errorBack(error);
        });

    };

    LuxPagination.prototype.updateUrls = function(data) {
        // updateUrls creates an object containing the most
        // recent last and next links from the API

        if (data && data.data && data.data.last) {
            this.urls = {
                last: data.data.last,
                next: data.data.next ? data.data.next : false
            };
            // If the recursive param was set to true this will
            // request data using the 'next' link; if not it will emitEvent
            // so the component knows there's more data available
            if (this.recursive) this.loadMore();
            else this.emitEvent();
        }

    };

    LuxPagination.prototype.emitEvent = function() {
        // emit event if more data available, the component can
        // listen for it and choose how to deal with it
        this.scope.$emit('moreData');
    };

    LuxPagination.prototype.loadMore = function() {
        // loadMore applies new urls from updateUrls to the
        // target object and makes another getData request.

        if (!this.urls.next && !this.urls.last) throw 'Updated URLs not set.';

        if (this.urls.next === false) {
            this.target.url = this.urls.last;
        } else if (this.urls.next) {
            this.target.url = this.urls.next;
        }

        // Call API with updated target URL
        this.getData(this.params);

    };

    LuxPagination.prototype.search = function(query, searchField) {
        this.searchField = searchField;
        this.params = this.params || {};
        this.params[this.searchField] = query;
        // Set current target URL to the original target URL to reset any
        // existing limits/offsets so full endpoint is searched
        this.target.url = this.orgUrl;

        this.getData(this.params);
    };

});
